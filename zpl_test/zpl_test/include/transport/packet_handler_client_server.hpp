#include <string>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <transport/packet_receiver.h>
#include <transport/packet_sender.h>
#include <boost/log/trivial.hpp>
#include <boost/format.hpp>
#include <boost/bind.hpp>
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <arpa/inet.h>

using namespace std;
using namespace zhicloud::transport;

class PacketHandlerClientServer{
public:
    PacketHandlerClientServer(const size_t& pkg_count, const size_t& pkg_size, const string& ip, const uint16_t& port):
        packet_size(pkg_size), packet_count(pkg_count), server_ip(ip), server_port(port),
        client_ip(ip), total_packet(pkg_count), total_byte(0),
        send_success(0), send_fail(0), send_byte(0), send_begin(false),
        received_packet(0), received_byte(0), receive_begin(false)
    {
        sender.bindHandler(boost::bind(&PacketHandlerClientServer::onPacketProcessed, this, _1, _2, _3, _4, _5, _6, _7));
        receiver.bindHandler(boost::bind(&PacketHandlerClientServer::onPacketReceived, this, _1, _2, _3, _4, _5, _6));
    }
    ~PacketHandlerClientServer(){}
    bool test(){
        int receive_socket(0), send_socket(0);
        {
            //builde up receiver
            receive_socket = socket(AF_INET, SOCK_DGRAM, 0);
            struct sockaddr_in address;
            address.sin_family = AF_INET;
            address.sin_port = htons(server_port);
            address.sin_addr.s_addr = inet_addr(server_ip.c_str());
            //set non-blocking
            if(!setNonBlocking(receive_socket)){
                return false;
            }
            if(-1 == bind(receive_socket, (sockaddr*)&address, sizeof(sockaddr))){
                BOOST_LOG_TRIVIAL(info)  << boost::format("can't bind to '%s:%d'") %server_ip %server_port;
                return false;
            }
            BOOST_LOG_TRIVIAL(info)  << boost::format("server bind to '%s:%d' success") %server_ip %server_port;
            receiver.addListener(receive_socket, server_ip, server_port);
            receiver.start();
            BOOST_LOG_TRIVIAL(info)  << "receiver started" ;
        }
        {
            //build up client
            send_socket = socket(AF_INET, SOCK_DGRAM, 0);
            struct sockaddr_in address;
            address.sin_family = AF_INET;
            address.sin_port = htons(0);
            address.sin_addr.s_addr = inet_addr(server_ip.c_str());
            //set non-blocking
            if(!setNonBlocking(send_socket)){
                return false;
            }
            if(-1 == bind(send_socket, (sockaddr*)&address, sizeof(sockaddr))){
                BOOST_LOG_TRIVIAL(info)  << boost::format("can't bind to '%s'") %server_ip;
                return false;
            }
            uint16_t local_port = address.sin_port;
            BOOST_LOG_TRIVIAL(info)  << boost::format("client bind to '%s:%d' success") %server_ip %local_port;
            sender.addSender(send_socket, server_ip, local_port);
            sender.start();
            BOOST_LOG_TRIVIAL(info)  << "sender started" ;
        }
        {
            //send packet
            {
                string packet_data(packet_size, 'z');
                chrono::time_point< chrono::high_resolution_clock > send_begin = chrono::high_resolution_clock::now();
                for(uint32_t i =0; i< packet_count;i++){
                    sender.send(packet_data, server_ip, server_port);
                }
                chrono::time_point< chrono::high_resolution_clock > send_end = chrono::high_resolution_clock::now();
                uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( send_end - send_begin).count();
                uint64_t put_speed = uint64_t(double(packet_count*1000000)/elapsed);
                BOOST_LOG_TRIVIAL(info)  << boost::format("put %d packet(s) in %.04f millisecond(s), speed %d /s")
                                                                %packet_count % (elapsed/1000 ) %put_speed;
            }
            {
                lock_type lock(event_mutex);
                send_finish_event.wait(lock);
            }
            BOOST_LOG_TRIVIAL(info)  << boost::format("send finished, %d success, %d fail") %send_success %send_fail;
            sender.stop();
            BOOST_LOG_TRIVIAL(info)  << "sender stopped";
            {
                //compute send result
                uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( last_send - first_send).count();
                uint64_t process_speed = uint64_t(double(send_success*1000000)/elapsed);
                double MiB_per_seconds = double(send_byte*1000000/1024/1024)/elapsed;
                BOOST_LOG_TRIVIAL(info)  << boost::format("%d packet(s) ( %d byte(s)) sent in %.04f millisecond(s)")
                                                                    %send_success %send_byte % (elapsed/1000 );
                BOOST_LOG_TRIVIAL(info)  << boost::format("speed: %d packet(s)/s, %.2f MiB/s")
                                                                    %process_speed % MiB_per_seconds;
                if(send_success != total_packet){
                    BOOST_LOG_TRIVIAL(error)  << boost::format("not all packet send success:%d / %d") %send_success %total_packet;
                    return false;
                }
            }
        }
        {
            //receive result
            const uint16_t max_timeout(5);
            lock_type lock(event_mutex);
            receive_finish_event.wait_for(lock, chrono::seconds(max_timeout));
            receiver.stop();
            BOOST_LOG_TRIVIAL(info)  << "receiver stopped";
            {
                uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( last_receive - first_receive).count();
                uint64_t packet_per_seconds = uint64_t(double(received_packet*1000000)/elapsed);
                double MiB_per_seconds = double(received_byte*1000000/1024/1024)/elapsed;
                BOOST_LOG_TRIVIAL(info)  << boost::format("%d packet(s) ( %d byte(s)) received in %.04f millisecond(s)")
                                                                    %received_packet %received_byte % (elapsed/1000 );
                BOOST_LOG_TRIVIAL(info)  << boost::format("speed: %d packet(s)/s, %.2f MiB/s")
                                                                    %packet_per_seconds % MiB_per_seconds;
            }
            //judge
            float lost = float(total_packet - received_packet)/total_packet;
            BOOST_LOG_TRIVIAL(error)  << boost::format("%d / %d packet received, lost %.02f%%") %received_packet %total_packet %(lost*100);
            if(lost > 0.05){
                return false;
            }
            close(receive_socket);
            close(send_socket);
            return true;
        }
    }

private:
    bool setNonBlocking(int socket){
        if(fcntl(socket, F_SETFL, fcntl(socket, F_GETFD, 0) | O_NONBLOCK) == -1){
            BOOST_LOG_TRIVIAL(info)  << "set non-blocking fail" ;
            return false;
        }
        return true;
    }
    void onPacketReceived(const std::string& data, const string& source_ip, const uint16_t& source_port, const string& target_ip, const uint16_t& target_port,  int socket){
        if(!receive_begin){
            first_receive = chrono::high_resolution_clock::now();
            receive_begin = true;
        }
        else{
            last_receive = chrono::high_resolution_clock::now();
        }
        received_byte += data.size();
        received_packet ++;
        if(received_packet >= total_packet){
            //receive finished
            lock_type lock(event_mutex);
            receive_finish_event.notify_all();
        }
    }
    void onPacketProcessed(bool success, const int& bytes, const string& to_ip, const uint16_t& to_port, const string& from_ip, const uint16_t& from_port,  const int& socket){
//        BOOST_LOG_TRIVIAL(info)  << boost::format("packet to '%s:%d' processed, result:%s")
//                                                                    %to_ip % to_port %success;
        if(!send_begin){
            first_send = chrono::high_resolution_clock::now();
            send_begin = true;
        }
        else{
            last_send = chrono::high_resolution_clock::now();
        }
        if(success){
            send_success++;
            send_byte += bytes;
        }
        else{
            send_fail++;
        }
        if((send_success + send_fail) >= total_packet){
            lock_type lock(event_mutex);
            send_finish_event.notify_all();
        }

    }

private:
    size_t packet_size;
    size_t packet_count;
    string server_ip;
    uint16_t server_port;
    string client_ip;
    uint64_t total_packet;
    uint64_t total_byte;
    //for send variable
    uint64_t send_success;
    uint64_t send_fail;
    uint64_t send_byte;
    bool send_begin;
    chrono::time_point< chrono::high_resolution_clock > first_send;
    chrono::time_point< chrono::high_resolution_clock > last_send;
    PacketSender sender;

    //for receive variable
    uint64_t received_packet;
    uint64_t received_byte;
    bool receive_begin;
    chrono::time_point< chrono::high_resolution_clock > first_receive;
    chrono::time_point< chrono::high_resolution_clock > last_receive;
    PacketReceiver receiver;

    mutex event_mutex;
    typedef unique_lock< mutex > lock_type;
    condition_variable send_finish_event;
    condition_variable receive_finish_event;
};

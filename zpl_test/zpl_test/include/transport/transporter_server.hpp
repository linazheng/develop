#ifndef TRANSPORTER_SERVER_H__
#define TRANSPORTER_SERVER_H__


#include <string>
#include <chrono>
#include <mutex>
#include <transport/transporter.h>
#include <util/define.hpp>
#include <transport/app_message.h>
#include <boost/log/trivial.hpp>
#include <boost/format.hpp>
#include <boost/bind.hpp>

using namespace std;
using namespace zhicloud::transport;
using namespace zhicloud::util;

class TransporterServer{

public:
    TransporterServer(const string& server_ip, const uint16_t& server_port):
        packet_count(0), packet_size(0), server_ip(server_ip), server_port(server_port),
        server("server"), received_packet(0), received_byte(0), connected(false), data_begin(false), summary(0),
        success(false)
    {
        server.bindMessageHandler(boost::bind(&TransporterServer::onMessageReceived, this, _1, _2));
    }
    ~TransporterServer(){
        //finish test
        server.stop();
    }
    bool build(){
        if(!server.bind(server_ip, server_port, 1)){
            BOOST_LOG_TRIVIAL(error)  << boost::format("can't bind to '%s:%d'") %server_ip % server_port;
            return false;
        }
        server.start();
        BOOST_LOG_TRIVIAL(info)  << boost::format("server start at '%s:%d'") %server_ip %server_port;
        return true;
    }
    bool waitResult(const size_t& timeout){
        lock_type lock(event_mutex);
        finish_event.wait_for(lock, chrono::seconds(timeout));
        uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( last_receive - first_receive).count();
        uint64_t packet_per_seconds = uint64_t(double(received_packet*1000000)/elapsed);
        double MiB_per_seconds = double(received_byte*1000000/1024/1024)/elapsed;
        BOOST_LOG_TRIVIAL(info)  << boost::format("%d packet(s) ( %d byte(s)) received in %.04f millisecond(s)")
                                                            %received_packet %received_byte % (elapsed/1000 );
        BOOST_LOG_TRIVIAL(info)  << boost::format("speed: %d packet(s)/s, %.2f MiB/s")
                                                            %packet_per_seconds % MiB_per_seconds;
        return success;
    }
private:
    void onMessageReceived(AppMessage& msg, const uint32_t& session_id){
        if(EventEnum::ready == (EventEnum)msg.id){
            //ready
            packet_count = msg.getUInt(ParamEnum::count);
            packet_size = msg.getUInt(ParamEnum::size);
            uint64_t send = msg.getUInt(ParamEnum::timestamp);
            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count() - send;
            BOOST_LOG_TRIVIAL(info)  << boost::format("transport started, packet size %d, count %d, delay %d millisecond(s)")
                                                                    %packet_size %packet_count % elapsed;
            return;
        }
        else if(EventEnum::data == (EventEnum)msg.id){
            if(!data_begin){
                first_receive = chrono::high_resolution_clock::now();
                data_begin = true;
            }
            else{
                last_receive = chrono::high_resolution_clock::now();
            }
            //data
            string packet_data;
            if(!msg.getString(ParamEnum::data, packet_data)){
                BOOST_LOG_TRIVIAL(error)  <<  "can't get packet data";
                return;
            }
            if(packet_data.size() != packet_size){
                BOOST_LOG_TRIVIAL(error)  << boost::format("invalid data received: %d / %d")
                                                                    %packet_data.size() %packet_size;
                return;
            }
            received_packet++;
            received_byte += packet_size;
            summary += msg.getUInt(ParamEnum::identity);
        }
        else if(EventEnum::finish == (EventEnum)msg.id){
            //finish
            uint64_t send_count = msg.getUInt(ParamEnum::count);
            uint64_t send_summary = msg.getUInt(ParamEnum::identity);
            uint64_t send = msg.getUInt(ParamEnum::timestamp);
            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count() - send;
            BOOST_LOG_TRIVIAL(info)  << boost::format("transport finished, delay %d millisecond(s)") % elapsed;

            if(send_count != received_packet){
                BOOST_LOG_TRIVIAL(error)  << boost::format("not all packet received: %d / %d")
                                                                    %received_packet %send_count;
            }
            else if(send_summary != summary){
                BOOST_LOG_TRIVIAL(error)  << boost::format("summary unmatched: %d / %d")
                                                                    %summary %send_summary;
            }
            else{
                BOOST_LOG_TRIVIAL(info) << boost::format("all packet received: %d")
                                                                    %received_packet;
                success = true;
            }
            lock_type lock(event_mutex);
            finish_event.notify_all();
            return;
        }

    }
//    void onServerConnected(const string& endpoint_name, const uint32_t& session_id){
//        BOOST_LOG_TRIVIAL(info)  << boost::format("'%s'[%08X] connected") %endpoint_name %session_id;
//        connected_event.set();
//        connected = true;
//        {
//            //begin message
//            AppMessage ready(AppMessage::message_type::EVENT, EventEnum::ready);
//            ready.setUInt(ParamEnum::count, packet_count);
//            ready.setUInt(ParamEnum::size, packet_size);
//            //begin time
//            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count();
//            ready.setUInt(ParamEnum::timestamp, elapsed);
//            client.sendMessage(session_id, ready);
//        }
//        uint64_t summary(0);
//        {
//            //data message
//            string packet_data(packet_size, 'z');
//            AppMessage data(AppMessage::message_type::EVENT, EventEnum::data);
//            data.setString(ParamEnum::data, packet_data);
//
//            chrono::time_point< chrono::high_resolution_clock > send_begin = chrono::high_resolution_clock::now();
//
//            for(uint64_t value =0; value< packet_count;value++){
//                data.setUInt(ParamEnum::identity, value);
//                if(client.sendMessage(session_id, data)){
//                    success_count++;
//                    summary += value;
//                }
//                else{
//                    fail_count++;
//                }
//            }
//            uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - send_begin).count();
//            uint64_t packet_speed = uint64_t(double(success_count*1000000)/elapsed);
//            double data_speed = double(success_count*packet_size*1000000/1024/1024)/elapsed;
//            BOOST_LOG_TRIVIAL(info)  << boost::format("%d packet(s) ( %d byte(s)) sent in %.04f millisecond(s)")
//                                                                    %success_count %(success_count*packet_size) % (elapsed/1000 );
//            BOOST_LOG_TRIVIAL(info)  << boost::format("speed: %d packet(s)/s, %.2f MiB/s")
//                                                                %packet_speed % data_speed;
//        }
//        {
//            //stop message
//            AppMessage finish(AppMessage::message_type::EVENT, EventEnum::finish);
//            finish.setUInt(ParamEnum::count, success_count);
//            finish.setUInt(ParamEnum::identity, summary);
//            //begin time
//            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count();
//            finish.setUInt(ParamEnum::timestamp, elapsed);
//            client.sendMessage(session_id, finish);
//        }
//    }
private:
    size_t packet_count;
    size_t packet_size;
    string server_ip;
    uint16_t server_port;
    Transporter server;
    size_t received_packet;
    size_t received_byte;
    bool connected;
    bool data_begin;
    chrono::time_point< chrono::high_resolution_clock > first_receive;
    chrono::time_point< chrono::high_resolution_clock > last_receive;
    uint64_t summary;
    bool success;
    mutex event_mutex;
    typedef unique_lock< mutex > lock_type;
    condition_variable finish_event;
};

#endif // TRANSPORTER_SERVER_H__


#ifndef TRANSPORTER_CLIENT_H__
#define TRANSPORTER_CLIENT_H__

#include <string>
#include <chrono>
#include <mutex>
#include <service/event.hpp>
#include <transport/transporter.h>
#include <util/define.hpp>
#include <transport/app_message.h>
#include <boost/log/trivial.hpp>
#include <boost/format.hpp>
#include <boost/bind.hpp>

using namespace std;
using namespace zhicloud::transport;
using zhicloud::service::Event;
using namespace zhicloud::util;

class TransporterClient{

public:
    TransporterClient(const size_t& pkg_count, const size_t& pkg_size, const string& ip, const string& server_ip, const uint16_t& server_port):
        packet_count(pkg_count), packet_size(pkg_size), client_ip(ip), server_ip(server_ip), server_port(server_port),
        client("client"), success_count(0), fail_count(0), connected(false)
    {
        client.bindConnectedHandler(boost::bind(&TransporterClient::onServerConnected, this, _1, _2));
    }
    ~TransporterClient(){
        //finish test
        client.stop();
    }
    bool build(){
        if(!client.bind(client_ip)){
            BOOST_LOG_TRIVIAL(error)  << boost::format("can't bind to '%s'") %client_ip;
            return false;
        }
        client.start();
        BOOST_LOG_TRIVIAL(info)  << boost::format("client start at '%s:%d'") %client_ip %client.getPort();
        uint32_t id = 0;
        if(!client.tryConnect("server", server_ip, server_port, id)){
            BOOST_LOG_TRIVIAL(error)  << boost::format("try connect to '%s:%d' fail") %server_ip %server_port;
            return false;
        }
        return true;
    }
    bool waitConnected(const uint16_t& timeout){
        connected_event.wait();
        return true;
    }
private:
    void onServerConnected(const string& endpoint_name, const uint32_t& session_id){
        BOOST_LOG_TRIVIAL(info)  << boost::format("'%s'[%08X] connected") %endpoint_name %session_id;
        connected_event.set();
        connected = true;
        {
            //begin message
            AppMessage ready(AppMessage::message_type::EVENT, EventEnum::ready);
            ready.setUInt(ParamEnum::count, packet_count);
            ready.setUInt(ParamEnum::size, packet_size);
            //begin time
            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count();
            ready.setUInt(ParamEnum::timestamp, elapsed);
            client.sendMessage(session_id, ready);
        }
        uint64_t summary(0);
        {
            //data message
            string packet_data(packet_size, 'z');
            AppMessage data(AppMessage::message_type::EVENT, EventEnum::data);
            data.setString(ParamEnum::data, packet_data);

            chrono::time_point< chrono::high_resolution_clock > send_begin = chrono::high_resolution_clock::now();

            for(uint64_t value =0; value< packet_count;value++){
                data.setUInt(ParamEnum::identity, value);
                if(client.sendMessage(session_id, data)){
                    success_count++;
                    summary += value;
                }
                else{
                    fail_count++;
                }
            }
            uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - send_begin).count();
            uint64_t packet_speed = uint64_t(double(success_count*1000000)/elapsed);
            double data_speed = double(success_count*packet_size*1000000/1024/1024)/elapsed;
            BOOST_LOG_TRIVIAL(info)  << boost::format("%d packet(s) ( %d byte(s)) sent in %.04f millisecond(s)")
                                                                    %success_count %(success_count*packet_size) % (elapsed/1000 );
            BOOST_LOG_TRIVIAL(info)  << boost::format("speed: %d packet(s)/s, %.2f MiB/s")
                                                                %packet_speed % data_speed;
        }
        {
            //stop message
            AppMessage finish(AppMessage::message_type::EVENT, EventEnum::finish);
            finish.setUInt(ParamEnum::count, success_count);
            finish.setUInt(ParamEnum::identity, summary);
            //begin time
            uint64_t elapsed = chrono::duration_cast< chrono::milliseconds >(chrono::high_resolution_clock::now().time_since_epoch()).count();
            finish.setUInt(ParamEnum::timestamp, elapsed);
            client.sendMessage(session_id, finish);
        }
    }
private:
    Event connected_event;
    size_t packet_count;
    size_t packet_size;
    string client_ip;
    string server_ip;
    uint16_t server_port;
    Transporter client;
    size_t success_count;
    size_t fail_count;
    bool connected;
};

#endif // TRANSPORTER_CLIENT_H__

#ifndef PACKET_SENDER_H
#define PACKET_SENDER_H

#include <map>
#include <string>
#include <thread>
#include <boost/signals2.hpp>
#include <service/runable.hpp>
#include <service/active_queue.hpp>
#include <service/passive_queue.hpp>

using namespace zhicloud::service;
using std::string;

namespace zhicloud{
    namespace transport{
        class PacketSender: public Runable
        {
            private:
                class SenderInfo{
                    public:
                        SenderInfo();
                        SenderInfo(const int& socket_fd, const std::string& ip, const uint16_t& port);
                        ~SenderInfo();
                        SenderInfo(SenderInfo&& other);
                        SenderInfo& operator=(SenderInfo&& other);
                        const std::string& getSourceIP() const;
                        const uint16_t& getSourcePort() const;
                    private:
                        int socket_id;
                        std::string source_ip;
                        uint16_t source_port;
                };
                class PacketData{
                    public:
                        PacketData();
                        PacketData(const string& data, const string& s_ip, const uint16_t& s_port, const string& d_ip, const uint16_t& d_port,  const int& socket);
                        ~PacketData();
                        PacketData(PacketData&& other);
                        PacketData& operator=(PacketData&& other);
                        PacketData(const PacketData& other);
                        PacketData& operator=(const PacketData& other);
                        const string& getData() const;
                        const string& getTargetIP() const;
                        const uint16_t& getTargetPort() const;
                        const string& getSourceIP() const;
                        const uint16_t& getSourcePort() const;
                        const int& getSocketID() const;
                    private:
                        std::string data;
                        int socket_id;
                        std::string target_ip;
                        uint16_t target_port;
                        std::string source_ip;
                        uint16_t source_port;
                };
            public:
                typedef std::string address_type;
                typedef uint16_t port_type;
                typedef boost::signals2::signal< void (bool,  const int&,  const address_type&, const port_type&, const address_type&, const port_type&,  const int& ) > event_type;
                typedef event_type::slot_type event_handler;
                PacketSender(const uint16_t& send_thread = 1);
                virtual ~PacketSender();
                void addSender(int socket_fd, const address_type& address, const port_type& port);
                void send(const string& data, const address_type& target_ip, const port_type& target_port, const int& socket = 0);
                void bindHandler(const event_handler& handler);
            protected:
                virtual bool onStart();
                virtual void onStopping();
                virtual void onWaitFinish();
            private:
                void onPacketAvailable(PacketData& packet, uint64_t& pos, bool end_of_batch);
//                void monitorProcess();
                void activeSocket(int socket_id);
            private:
                const static size_t socket_buffer_size = 64;
                const static size_t packet_buffer_size = 1024;
                PassiveQueue< int, socket_buffer_size > socket_queue;
                std::map< int, SenderInfo > sender_map;
                ActiveQueue< PacketData, packet_buffer_size > packet_queue;
                std::thread monitor_thread;
                event_type onPacketProcessed;
        };

    }
}


#endif // PACKET_RECEIVER_H

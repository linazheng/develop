#ifndef PACKET_RECEIVER_H
#define PACKET_RECEIVER_H

#include <map>
#include <string>
#include <thread>
#include <boost/signals2.hpp>
#include <service/runable.hpp>
#include <service/active_queue.hpp>

using namespace zhicloud::service;
using std::string;

namespace zhicloud{
    namespace transport{
        class PacketReceiver: public Runable
        {
            private:
                class ListenerInfo{
                    public:
                        ListenerInfo();
                        ListenerInfo(const int& socket_fd, const std::string& ip, const uint16_t& port);
                        ~ListenerInfo();
                        ListenerInfo(ListenerInfo&& other);
                        ListenerInfo& operator=(ListenerInfo&& other);
                        const std::string& getListenIP() const;
                        const uint16_t& getListenPort() const;
                    private:
                        int socket_id;
                        std::string listen_ip;
                        uint16_t listen_port;
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
                        std::string destination_ip;
                        uint16_t destination_port;
                        std::string source_ip;
                        uint16_t source_port;
                };
            public:
                typedef std::string address_type;
                typedef uint16_t port_type;
                typedef boost::signals2::signal< void (const std::string&, const address_type&, const port_type&, const address_type&, const port_type&,  int ) > event_type;
                typedef event_type::slot_type event_handler;
                PacketReceiver(const uint16_t& receive_thread = 1);
                virtual ~PacketReceiver();
                void addListener(int socket_fd, const std::string& address, const uint16_t& port);
                void bindHandler(const event_handler& handler);
            protected:
                virtual bool onStart();
                virtual void onStopping();
                virtual void onWaitFinish();
            private:
                void onPacketReceivable(int& socket_fd, uint64_t& pos, bool end_of_batch);
                void onPacketAvailable(PacketData& packet, uint64_t& pos, bool end_of_batch);
                void monitorProcess();
            private:
                const static size_t socket_buffer_size = 16;
                const static size_t packet_buffer_size = 1024;
                const static size_t receive_buffer_size = 64*1024;//64 KiB
                ActiveQueue< int, socket_buffer_size > socket_queue;
                std::map< int, ListenerInfo > listener_map;
                ActiveQueue< PacketData, packet_buffer_size > packet_queue;
                event_type onPacketReceived;
                std::thread monitor_thread;
                char receive_buffer[receive_buffer_size];
        };

    }
}


#endif // PACKET_RECEIVER_H

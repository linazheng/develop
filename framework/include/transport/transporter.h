#ifndef TRANSPORTER_H
#define TRANSPORTER_H

#include <string>
#include <vector>
#include <set>
#include <random>
#include <thread>
#include <mutex>
#include <service/active_queue.hpp>
#include <service/runable.hpp>
#include <service/timed_invoker.h>
#include <util/logging.h>
#include <transport/endpoint_manager.h>
#include <transport/app_message.h>
#include <transport/command.h>
#include <transport/datagram.h>
#include <transport/task_manager.h>
#include <transport/endpoint_address.hpp>
#include <transport/packet_receiver.h>
#include <transport/packet_sender.h>

using namespace std;
using namespace zhicloud::util;
using zhicloud::service::Runable;
using zhicloud::service::TimedInvoker;
using zhicloud::service::Event;
using zhicloud::service::ActiveQueue;

namespace zhicloud{
    namespace transport{
        class Transporter:public Runable
        {
            public:
                typedef uint16_t  port_type;
                typedef EndpointManager::session_id_type session_id_type;
                typedef boost::signals2::signal< void (const string&, const session_id_type&) > connection_event_type;
                typedef connection_event_type::slot_type connection_event_handler;
                typedef boost::signals2::signal< void (AppMessage&, const session_id_type&) > message_event_type;
                typedef message_event_type::slot_type message_event_handler;

                Transporter(const string& name, const uint16_t & max_socket = 1, const uint16_t & work_thread = 1);
                virtual ~Transporter();
                bool bind(const string& ip, const port_type & start_port =5600, const port_type & range = 200);
                const string& getIP() const;
                const port_type & getPort() const;
                bool sendMessage(const session_id_type& session_id, const AppMessage& message);
                bool batchSend(const session_id_type& session_id, const list<AppMessage>& message_list);
                bool sendMessage(const session_id_type& session_id, AppMessage&& message);
                bool batchSend(const session_id_type& session_id,  list<AppMessage>& message_list);

                void bindConnectedHandler(const connection_event_handler& handler);
                void bindDisconnectedHandler(const connection_event_handler& handler);
                void bindMessageHandler(const message_event_handler& handler);
                bool tryConnect(const string& remote_name, const string& ip, const port_type& port, session_id_type& session_id);
                bool tryDisconnect(const session_id_type& session_id);
                void disconnectAll();
                bool releaseSession(const session_id_type& session_id);
            protected:
                virtual bool onStart();
                virtual void onStopping();
                virtual void onWaitFinish();
                virtual void onStopped();
            private:
                typedef EndpointAddress address_type;
                typedef TaskManager::task_id_type task_id_type;
                typedef std::pair< session_id_type,  AppMessage > message_item_type;
                typedef std::pair< address_type ,  Command > command_item_type;
                typedef std::pair< address_type, string > packet_item_type;
                typedef std::pair< address_type, string > serilized_command_type;
                typedef std::unique_lock<std::mutex> lock_type;
                class DispatchEvent{
                public:
                    enum class EventType:uint16_t {
                        message = 0,
                        connected = 1,
                        disconnected = 2
                    };
                    DispatchEvent();
                    DispatchEvent(const EventType& type, const session_id_type& id, const string& name);
                	DispatchEvent(const EventType& type, const session_id_type& id, AppMessage&& msg);
                	~DispatchEvent();
                	DispatchEvent(DispatchEvent&& moved);
                	DispatchEvent& operator=(DispatchEvent& other);
                	DispatchEvent& operator=(DispatchEvent&& other);
                public:
                    string name;
                    EventType type;
                    session_id_type session_id;
                    AppMessage msg;
                };

                typedef DispatchEvent notify_item_type;
                bool sendCommand(Command& command, const string& remote_ip, const port_type& remote_port);
                bool sendCommand(Command& command, const session_id_type& session_id);

                //handle message
                void handleKeepAlive(Command& msg, const session_id_type& session_id);
                void handleConnectRequest(Command& msg, const address_type& remote_address, const session_id_type& session_id);
                void handleConnectResponse(Command& msg, const address_type& remote_address, const session_id_type& session_id);
                void handleConnectACK(Command& msg, const session_id_type& session_id);
                void handleDisconnectRequest(Command& msg, const session_id_type& session_id);
                void handleDisconnectResponse(Command& msg, const session_id_type& session_id);
                void handleMessageData(Command& msg, const session_id_type& session_id);
                string computeChallengeKey(const string& client_key) const;
                string computeVerifyDigest(const string& client_key, const string& challenge_key) const;
                void notifySessionConnected(const string& name, const session_id_type& session_id);
                void notifySessionDisconnected(const string& name, const session_id_type& session_id);
                void onTimedCheck();
                void onPacketProcessed(bool success,  const int& bytes,  const string& to_ip, const port_type& to_port,
                                                        const string& from_ip, const port_type& from_port,  const int& socket_id);
                void onPacketReceived(const std::string& data, const string& from_ip, const port_type& from_port,
                                                        const string& to_ip, const port_type& to_port,  int socket_id);
                bool setNonBlocking(int socket);
                void processAppMessage(message_item_type& item, uint64_t& pos, bool end_of_batch);
                void processSerilizedCommand(serilized_command_type& item, uint64_t& pos, bool end_of_batch);

                void processReceivedPacket(packet_item_type& item, uint64_t& pos, bool end_of_batch);
                void processReceivedCommand(command_item_type& item, uint64_t& pos, bool end_of_batch);
                void processNotifyEvent(notify_item_type& item, uint64_t& pos, bool end_of_batch);

                connection_event_type onSessionConnected;
                connection_event_type onSessionDisconnected;
                message_event_type onMessageReceived;
            private:
                static const uint32_t max_datagram_size;
                static const uint32_t max_message_size;
                static const uint32_t check_interval_in_milli;
                string name;
                uint16_t max_socket;
                string local_ip;
                uint16_t  local_port;
                string server_key;
                vector< int > socket_vector;
                logger_type logger;
                EndpointManager endpoint_manager;
                TaskManager task_manager;

                default_random_engine generator;
                uniform_int_distribution<unsigned int> key_distribution;

                TimedInvoker invoker;
                unsigned int check_counter;

                PacketReceiver receiver;
                PacketSender sender;
                const static size_t ring_buffer_size = 1024;
                ActiveQueue< message_item_type, ring_buffer_size > _serialize_queue;
                ActiveQueue< serilized_command_type, ring_buffer_size > _package_queue;

                ActiveQueue< packet_item_type, ring_buffer_size > _unpackage_queue;
                ActiveQueue< command_item_type, ring_buffer_size > _unserialize_queue;
                ActiveQueue< notify_item_type, ring_buffer_size > _notify_queue;
        };
    }
}
#endif // TRANSPORTER_H

#ifndef NODESERVICE_H
#define NODESERVICE_H

#include <string>
#include <map>
#include <list>
#include <set>
#include <mutex>
#include <boost/signals2.hpp>
#include <util/define.hpp>
#include <util/domain_utility.h>
#include <util/logging.h>
#include <transport/app_message.h>
#include <transport/transporter.h>
#include <service/timer_service.h>
#include <service/active_queue.hpp>

using namespace zhicloud::util;
using namespace zhicloud::transport;
using namespace std;

namespace zhicloud{
    namespace service{
        class NodeService
        {
            public:
                typedef boost::signals2::signal< void (const string&, const string&) > config_event_type;
                typedef config_event_type::slot_type config_event_handler;
                typedef uint16_t port_type;
                typedef TimerService::timer_id_type timer_id_type;
                typedef uint32_t session_id_type;
                typedef uint32_t endpoint_id_type;
                typedef uint32_t timeout_type;

                NodeService(const ServiceType& service_type, const string& service_name, const string& domain_name, const string& local_ip,
                            const uint16_t& start_port, const uint16_t& port_range, const string& group_ip, const uint16_t& group_port,
                            const string& version, const string& server_id = "", const string& rack_id = "", const string& server_name = "",
                            const uint32_t& max_socket = 1, const uint32_t& transport_thread = 1);
                virtual ~NodeService();
                bool start();
                void stop();
                bool connectEndpoint(const string& endpoint_name, const ServiceType& service_type,
                                     const string& remote_ip, const port_type& remote_port, const string& group = "default");
                void bindServiceModifiedHandler(const config_event_handler& handler);
                void bindServerModifiedHandler(const config_event_handler& handler);
                //put to tail
                bool putMessage(const AppMessage& msg, const string& sender);
                bool putMessage(const AppMessage& msg);
                //put to head
                bool insertMessage(const AppMessage& msg, const string& sender);
                bool putMessage(const list< AppMessage >& msg_list, const string& sender);
                bool sendMessage(AppMessage& msg, const string& receiver);
                bool sendToDomainServer(AppMessage& msg);
                timer_id_type setTimer(const timeout_type& timeout, const session_id_type& receive_session);
                timer_id_type setLoopTimer(const timeout_type& timeout, const session_id_type& receive_session);
                timer_id_type setTimedEvent(const AppMessage& event, const timeout_type& timeout);
                timer_id_type setLoopTimedEvent(const AppMessage& event, const timeout_type& timeout);
                bool clearTimer(const timer_id_type& timer_id);
            protected:
                void console(const string& content);
                void console(boost::format& input);

                //need override
                virtual bool onStart();
                virtual void onStop();
                virtual void onChannelConnected(const string& endpoint_name, const ServiceType& service_type, const string& remote_ip, const port_type& remote_port);
                virtual void onChannelDisconnected(const string& endpoint_name, const ServiceType& service_type);
                virtual void onTransportEstablished(const string& local_ip, const port_type& local_port);
                virtual void handleEventMessage(AppMessage& msg, const string& sender);
                virtual void handleRequestMessage(AppMessage& msg, const string& sender);
                virtual void handleResponseMessage(AppMessage& msg, const string& sender);
                virtual void onDomainJoined();
                virtual void onDomainLeft();

            private:
                typedef std::pair< AppMessage, string > queue_item_type;
                struct EndpointEntry{
                    string name;
                    string ip;
                    port_type port;
                    ServiceType type;
                    string domain;
                    string group;
                    endpoint_id_type endpoint_id;
                    bool allocated;
                    bool connected;
                };
                void onEndpointMessageReceived(AppMessage& msg, const endpoint_id_type& endpoint_id);
                void onEndpointConnected(const string& endpoint_name, const endpoint_id_type& endpoint_id);
                void onEndpointDisconnected(const string& endpoint_name, const endpoint_id_type& endpoint_id);
                void onTimeoutEvent(list< AppMessage >& msg_list);
                void onMessageAvailable(queue_item_type& item, uint64_t& pos, bool end_of_batch);
                bool allocateEndpoint(const string& endpoint_name, const endpoint_id_type& endpoint_id);
                bool allocateEndpoint(const string& endpoint_name);
                bool deallocateEndpoint(const string& endpoint_name);
                EndpointEntry& getEndpoint(const string& endpoint_name);
                bool disconnectEndpoint(const string& endpoint_name);
                bool isSystemMessage(const AppMessage& msg) const;
                void handleSystemMessage(AppMessage& msg, const string& sender);
                void handleServiceUpdate(AppMessage& msg, const string& sender);
                bool joinDomain(const string& data_server);
                void onJoinDomainResponse(AppMessage& msg, const string& sender);
                bool leaveDomain();
                void onLeaveDomainResponse(AppMessage& msg, const string& sender);
                void onServiceAvailable(const string& service_name, const string& service_ip,
                                        const port_type& service_port, const string& local_ip);
                void handleServiceAvailable(const string& service_name, const string& service_ip,
                                            const port_type& service_port, const string& sender);
                void onDataServerDisconnected(const string& service_name);
                void onCheckService();
                bool disableServiceCheck();
                bool enableServiceCheck();
                void onConnectResponse(AppMessage& msg, const string& sender);
                void onConnectRequest(AppMessage& msg, const string& sender);
                void onDisconnectResponse(AppMessage& msg, const string& sender);
                void onDisconnectRequest(AppMessage& msg, const string& sender);
                void disonnectAllEndpoint();
                config_event_type onServiceModified;
                config_event_type onServerModified;

            protected:
                string rack_id;
                string server_id;
                string server_name;
                string domain_name;
                string service_group;
                string service_name;
                ServiceType service_type;
                string version;
                string local_ip;
                port_type local_port;
                string fullname;
                logger_type logger;

            private:
                typedef std::lock_guard< std::recursive_mutex > lock_type;
                const static timeout_type service_check_interval;
                port_type start_port;
                port_type port_range;
                string domain_server;
                bool domain_connected;
                bool transport_established;
                timer_id_type service_check_timer;
                std::recursive_mutex endpoint_mutex;
                map< string, EndpointEntry > endpoint_map;
                map< endpoint_id_type, string > endpoint_id_map;
                map< ServiceType, set < string > > active_service;
                Transporter transporter;
                TimerService timer_service;
                DomainUtility domain_utility;
                const static size_t queue_size = 4*1024;
                ActiveQueue< queue_item_type, queue_size > message_queue;
        };

    }
}


#endif // NODESERVICE_H

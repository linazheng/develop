#ifndef MAIN_SERVICE_H
#define MAIN_SERVICE_H

#include <string>
#include <util/define.hpp>
#include <util/logging.h>
#include <transport/app_message.h>
#include <service/node_service.h>
#include <service/service_proxy.h>

using namespace std;

namespace zhicloud
{
    namespace control_server{

        class MainService: public NodeService
        {
        public:
            MainService(const string& service_name, const string& domain, const string& ip, const string& group_ip, const uint16_t& group_port, const string& server,
                        const string& rack, const string& server_name);
            ~MainService();
            bool initialize();
            bool onStart();
            void onStop();
            void onChannelConnected(const string& node_name, const ServiceType& node_type, const string& remote_ip, const uint16_t& remote_port);
            void onChannelDisconnected(const string& node_name, const ServiceType& node_type);
            void handleEventMessage(AppMessage& event, const string& sender);
            void handleRequestMessage(AppMessage& request, const string& sender);
            void handleResponseMessage(AppMessage& response,const string& sender);
            void onTransportEstablished(const string& ip, const uint16_t& port);
            void handleTimeout(AppMessage& event, const string& sender);
            void handleNotifyTimeout();

        private:
            const static string version;
            const static string config_root;

            const static uint32_t monitor_timer_session;
            static uint32_t monitor_timer_id;
            const static uint32_t monitor_interval;

            const static uint32_t status_timer_session;
            static uint32_t status_timer_id;
            const static uint32_t status_interval;

            const static uint32_t statistic_timer_session;
            static uint32_t statistic_timer_id;
            const static uint32_t statistic_interval;

            const static uint32_t synchronize_timer_session;
            static uint32_t synchronize_timer_id;
            const static uint32_t synchronize_interval;

            const static uint32_t storage_server_timer_session;
            static uint32_t storage_server_timer_id;
            const static uint32_t storage_server_interval;
        };
    }
}
#endif // MAIN_SERVICE_H

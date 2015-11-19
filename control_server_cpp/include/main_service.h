#ifndef MAIN_SERVICE_H
#define MAIN_SERVICE_H

#include <string>
#include <set>
#include <map>
#include <util/define.hpp>
#include <util/logging.h>
#include <transport/app_message.h>
#include <service/node_service.h>
#include <service/service_proxy.h>
#include "computepool_manager.h"
#include "clienttrans_manager.h"
#include "status_manager.h"
#include "config_manager.h"
#include "monitor_manager.h"
#include "service_manager.h"
#include "expire_manager.h"

/*#include "address_manager.h"
#include "port_manager.h"
#include "storage_manager.h"
#include "snapshotpool_manager.h"
#include "forwarder_manager.h"
#include "iso_manager.h"
#include "network_manager.h"*/

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
            void handleNotifyTimeout();

        protected:
            void onClientConnected(const string& node_name);
            void onDataServerConnected(const string& node_name);
            void onStorageConnected(const string& node_name);
            void onIntelligentRouterConnected(const string& node_name);
            void onDataIndexConnected(const string& node_name);

            void onClientDisconnected(const string& node_name);
            void onStorageDisconnected(const string& node_name);
            void onIntelligentRouterDisconnected(const string& node_name);
            void onStatisticServerDisconnected(const string& node_name);

            void handleTimeout(AppMessage& event, const string& sender);
            void handleServiceStatusChanged(AppMessage& event, const string& sender);
            void handleMonitorHeartBeat(AppMessage& event, const string& sender);
            void handleKeepAlive(AppMessage& event, const string& sender);
            void handleStartMonitorRequest(AppMessage& event, const string& sender);
            void handleStopMonitorRequest(AppMessage& event, const string& sender);
            void handleStartStatisticRequest(AppMessage& event, const string& sender);
            void handleStopStatisticRequest(AppMessage& event, const string& sender);

            void handleStatisticKeepAlive();
            void handleMonitorTimeout();
            void handleStatisticCheckTimeout();
            void handleSynchronizeTimeout();
            void handleStorageServerSyncTimeout();
            void onStatusCheckTimeout();
            void reportStatisticData();

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

            const static uint32_t _transaction_thread;

            boost::shared_ptr<ComputePoolManager> _computepool_manager;
            boost::shared_ptr<ClientTransManager> _clienttrans_manager;
            boost::shared_ptr<StatusManager> _status_manager;
            boost::shared_ptr<ConfigManager> _config_manager;
            boost::shared_ptr<MonitorManager> _monitor_manager;
            boost::shared_ptr<ServiceManager> _service_manager;
            boost::shared_ptr<ExpireManager> _expire_manager;

            uint32_t _statistic_timeout;
            string _statistic_server;
            const static uint32_t _max_statistic_timeout;
            /*boost::shared_ptr<AddressManager> _address_manager;
            boost::shared_ptr<PortManager> _port_manager;
            boost::shared_ptr<StorageManager> _storage_manager;
            boost::shared_ptr<SnapshotPoolManager> _snapshotpool_manager;
            boost::shared_ptr<ForwarderManager> _forwarder_manager;
            boost::shared_ptr<ISOManager> _iso_manager;
            boost::shared_ptr<NetworkManager> _network_manager;*/

            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _storage_server_mutex;
            mutable recursive_mutex _intelligent_router_mutex;
            mutable recursive_mutex _data_indexes_mutex;

            map<string,uint32_t> _sync_session; //key = node name,value = session_id
            map<string,uint32_t> _observe_session; //key = node name,value = session_id

            set<string> _storage_server;
            set<string> _intelligent_router;
            set<string> _data_indexes;

        };
    }
}
#endif // MAIN_SERVICE_H

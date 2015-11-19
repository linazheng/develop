#ifndef STATUSMANAGER_H
#define STATUSMANAGER_H


#include <util/logging.h>
#include "server_status.hpp"
#include "compute_pool_status.hpp"
#include "system_status_message.hpp"
#include "host_status.hpp"

namespace zhicloud
{
    namespace control_server{

        class StatusManager
        {
        public:
            StatusManager(const string& logger_name);
            ~StatusManager();

            void checkTimeout();
            void updateServerStatus(const vector<ServerStatus>& value);
            void updateHostStatus(const vector<HostStatus>& value);
            void updateComputePoolStatus(const vector<ComputePoolStatus>& value);
            void updateServerRoomStatus(const vector<ServerRoomStatus>& value);
            void updateServerRackStatus(const vector<ServerRackStatus>& value);

            bool containsServerStatus(const UUID_TYPE& uuid);
            bool containsHostStatus(const UUID_TYPE& uuid);
            bool containsComputePoolStatus(const UUID_TYPE& uuid);
            bool containsServerRoomStatus(const UUID_TYPE& uuid);
            bool containsServerRackStatus(const UUID_TYPE& uuid);
            bool containsSystemStatus();

            bool getServerStatus(const UUID_TYPE& uuid, ServerStatus& value)const;
            bool getHostStatus(const UUID_TYPE& uuid, HostStatus& value)const;
            bool getComputePoolStatus(const UUID_TYPE& uuid, ComputePoolStatus& value)const;
            bool getServerRoomStatus(const UUID_TYPE& uuid, ServerRoomStatus& value)const;
            bool getServerRackStatus(const UUID_TYPE& uuid, ServerRackStatus& value)const;
            bool getSystemStatus(SystemStatusMessage& value)const;

            bool removeServerStatus(const UUID_TYPE& uuid);
            bool removeHostStatus(const UUID_TYPE& uuid);
            bool addHostStatus(const HostStatus& value);
            bool changeHostStatus(const UUID_TYPE& uuid, const UnitStatusEnum& _status);

            void getAllComputePoolStatus(vector<ComputePoolStatus>& list) const;
            void getAllServerRoomStatus(vector<ServerRoomStatus>& list) const;
            void getAllServerRackStatus(vector<ServerRackStatus>& list) const;
            void getAllServerStatus(vector<ServerStatus>& list)const;
            void getAllHostStatus(vector<HostStatus>& list)const;

            bool removeComputePoolStatus(const UUID_TYPE& uuid);
            void updateSystemStatus(const SystemStatusMessage& status);
            void statisticHostStatus(StatusCounter &counter)const;

        protected:
            StatusManager();
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            map<UUID_TYPE,ServerRoomStatus> _server_room_status;//key = room id, value = server room status
            map<UUID_TYPE,uint32_t> _server_room_counter;// ##key = room id, value = counter

            map<UUID_TYPE,ServerRackStatus> _server_rack_status;//key = rack id, value = server rack status
            map<UUID_TYPE,uint32_t> _server_rack_counter;// key = rack id, value = counter

            map<UUID_TYPE,ServerStatus> _server_status;//key = uuid, value = server status
            map<UUID_TYPE,uint32_t> _server_counter;//key = uuid, value = counter

              map<UUID_TYPE,HostStatus> _host_status;//key = uuid, value = host status
            map<UUID_TYPE,uint32_t> _host_counter;//key = uuid, value = counter

            map<UUID_TYPE,ComputePoolStatus> _compute_pool_status;//key = uuid, value = compute pool status
            map<UUID_TYPE,uint32_t> _compute_pool_counter;//key = uuid, value = counter

            SystemStatusMessage _status;
            const static uint32_t _max_timeout;

        };
    }
}

#endif // STATUSMANAGER_H

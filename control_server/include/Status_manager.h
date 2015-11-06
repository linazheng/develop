#ifndef STATUSMANAGER_H
#define STATUSMANAGER_H


#include <util/logging.h>
#include "Server_status.hpp"
#include "Compute_pool_status.hpp"
#include "System_status_message.hpp"


namespace zhicloud
{
    namespace control_server{

        class StatusManager
        {
        public:
            StatusManager(const string& logger_name);
            ~StatusManager();

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

            map<UUID_TYPE,ComputePoolStatus> _compute_pool_status;//key = uuid, value = compute pool status
            map<UUID_TYPE,uint32_t> _compute_pool_counter;//key = uuid, value = counter

            SystemStatusMessage _status;

        };
    }
}

#endif // STATUSMANAGER_H

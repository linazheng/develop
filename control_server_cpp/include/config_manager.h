#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H


#include <util/logging.h>

#include "server_info.hpp"
#include "host_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class ConfigManager{
        public:
            ConfigManager(const string &logger_name);
            ~ConfigManager();

            bool containsHost(const string& host);
            bool containsServer(const string& server);

        protected:
            ConfigManager(){}

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;

            util::logger_type _logger;

            map<UUID_TYPE,ServerRoomInfo> _server_rooms;
            map<UUID_TYPE,ServerRackInfo> _server_racks;
            map<UUID_TYPE,ServerInfo> _servers;
            map<UUID_TYPE,HostInfo> _hosts;
            map<uint32_t,HostInfo> _host_in_creating;//key = session id, value = host info

            map< UUID_TYPE, vector<UUID_TYPE> > _room_members;//##key = room id, value = list of rack id
            map< UUID_TYPE, vector<UUID_TYPE> > _rack_members;//##key = rack id, value = list of server id
            map< string, vector<UUID_TYPE> > _host_in_service;//key = service name, value = list of host id

        };
    }
}

#endif // CONFIG_MANAGER_H

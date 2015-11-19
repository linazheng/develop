#ifndef NETWORKMANAGER_H
#define NETWORKMANAGER_H

#include <util/logging.h>
#include "network_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class NetworkManager
        {
        public:
            NetworkManager(const string& resource_path,const string& logger_name);
            ~NetworkManager();

        protected:

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            string _pool_path;
            map<UUID_TYPE,NetworkInfo> _network_info;
            uint32_t _min_ip;
            uint32_t _max_ip;
            bool _is_sorted;
        };
    }
}

#endif // NETWORKMANAGER_H

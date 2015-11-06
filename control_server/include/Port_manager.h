#ifndef PORTMANAGER_H
#define PORTMANAGER_H

#include <util/logging.h>
#include "Port_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class PortManager
        {
        public:
            PortManager(const string& resource_path,const string& logger_name);
            ~PortManager();

        protected:
            PortManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            bool _modified;
            map<UUID_TYPE,PortPool>port_pool;
        };
    }
}
#endif // PORTMANAGER_H

#ifndef FORWARDERMANAGER_H
#define FORWARDERMANAGER_H


#include <util/logging.h>
#include "Host_forwarder.hpp"

namespace zhicloud
{
    namespace control_server{

        class ForwarderManager
        {
        public:
            ForwarderManager(const string& resource_path,const string& logger_name);
            ~ForwarderManager();

        protected:
            ForwarderManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            map<UUID_TYPE,HostForwarder> _forwarder;
            bool _modified;
            uint32_t _crc;
        };
    }
}
#endif // FORWARDERMANAGER_H

#ifndef SERVICEMANAGER_H
#define SERVICEMANAGER_H

#include <util/logging.h>
#include <util/define.hpp>
#include "Service_staus.hpp"

namespace zhicloud
{
    namespace control_server{

        class ServiceManager
        {
        public:
            ServiceManager(const string& logger_name);
            ~ServiceManager();

        protected:
            ServiceManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;


            map<util::ServiceType,vector<string>> _server_groups;//# #key = service type, value = {group:list of service name}
            map<string,ServiceStatus> _service_map;//key = service name, value = service
            map<UUID_TYPE,string> _service_in_server;//key = server uuid, value = service name
            map<string,WhisperService> _whispers;//key = service name, value = whisper service
        };
    }
}

#endif // SERVICEMANAGER_H

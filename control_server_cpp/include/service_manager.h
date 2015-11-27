#ifndef SERVICEMANAGER_H
#define SERVICEMANAGER_H

#include <util/logging.h>
#include <util/define.hpp>
#include "service_staus.hpp"

namespace zhicloud
{
    namespace control_server{

        class ServiceManager
        {
        public:
            ServiceManager(const string& logger_name);
            ~ServiceManager();

            bool activeService(const ServiceStatus& service);
            bool deactiveService(const ServiceStatus& service);
            bool containsService(const string& name);
            bool getService(const string& name,ServiceStatus& service)const;
            void loadService(const uint32_t& service_type, const vector<ServiceStatus>& service_list);
            void queryService(const uint32_t& service_type,const string& group_name,vector<ServiceStatus>& status_list)const;
            bool updateService(const string& service_name,const ComputeStorageTypeEnum& type);
            bool queryServicesInServer(const UUID_TYPE& server,vector<string>& service_list)const;
            void getAllServiceType(vector<uint32_t>& type_list)const;
            bool queryServiceGroup(const uint32_t& service_type,vector<string>& group_list)const;
            bool updateWhisper(const string& service_name,const vector<WhisperService>& whisper_list);
            bool containsWhisper(const string& service_name);
            bool getWhisper(const string& service_name,vector<WhisperService>& whisper_list)const;
            void getAllWhisper(vector<WhisperService>& whisper_list)const;
            void statisticStatus(StatusCounter &counter)const;

        protected:
            ServiceManager(){}
            void addService(const ServiceStatus& service);
            void deleteServiceFromServer(const UUID_TYPE& server_id,const string& service_name);
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;


            map<uint32_t,map<string,set<string>>> _server_groups;//# #key = service type, value = {group:list of service name}
            map<string,ServiceStatus> _service_map;//key = service name, value = service
            map<UUID_TYPE,set<string>> _service_in_server;//key = server uuid, value = service name list
            map<string,vector<WhisperService>> _whispers;//key = service name, value = whisper service list
        };
    }
}

#endif // SERVICEMANAGER_H

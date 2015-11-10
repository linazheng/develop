#ifndef SERVICEPROXY_H
#define SERVICEPROXY_H

#include <string>
#include <memory>
#include <service/node_service.h>
#include <util/define.hpp>
#include <util/generator.h>
#include <boost/uuid/random_generator.hpp>


#include <boost/filesystem.hpp>

using zhicloud::util::ServiceType;
using zhicloud::util::Generator;
using namespace std;
using namespace boost::filesystem;

namespace zhicloud{
    namespace service{
        class ServiceProxy
        {
            public:
                typedef int pid_type;
                ServiceProxy(const ServiceType& type);
                virtual ~ServiceProxy();
                bool start();
                void stop();
                bool isProcessRunning();
                bool getPID(pid_type& pid, string& cmd);
            protected:
                virtual NodeService* createService() = 0;
            private:
                ServiceProxy(const ServiceProxy& other);
                ServiceProxy& operator=(const ServiceProxy& other);
                void attachLogger();
                void redirectOutput();
                bool loadConfig();
                bool modifyService(const string& service_name, const string& domain_name);
                bool modifyServer(const string& server_name, const string& rack_id);
                void console(const string& content);
                void writeProcess();
                void eraseProcess();
                bool getProcessCommand(const pid_type& pid, string& cmd);
            protected:
                string service_name;
                string domain_name;
                string service_ip;
                string group_ip;
                uint16_t group_port;
                string server_id;
                string server_name;
                string rack_id;
            private:
                string type_name;
                ServiceType service_type;
                path root_path;
                path log_path;
                path running_path;
                path tmp_path;
                path config_path;
                path module_path;
                path config_file;
                path server_info;
                path out_file;
                path pidfile;
                string log_prefix;
                bool config_loaded;
                unique_ptr< NodeService > service;
                const string default_domain;
                const string default_multicast_ip;
                const uint16_t default_multicast_port;
                Generator generator;
        };
    }

}



#endif // SERVICEPROXY_H

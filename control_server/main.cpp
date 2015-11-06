#include <service/daemon.h>
#include <util/define.hpp>
#include <service/service_proxy.h>

#include "Main_service.h"

using namespace zhicloud::service;
using namespace zhicloud::control_server;

namespace zhicloud
{
    class Proxy: public ServiceProxy
    {
    public:
        Proxy():ServiceProxy(ServiceType::control_server)
        {

        }

        ~Proxy(){}

        NodeService* createService()
        {
            if(service_ip.empty() || service_name.empty())
            {
                cout << "must specify local ip and node name for control server "<< endl;
                return nullptr;
            }

            MainService* service = new MainService(service_name, domain_name, service_ip, group_ip, group_port,
                                                server_id, rack_id, server_name);
            return service;
        }
    };
}

using namespace zhicloud;

int main(int argc, char** argv)
{
    Proxy proxy;
    Daemon daemon(&proxy);


    if(argc == 2)
    {
        string param(argv[1]);
        if(param == "start")
        {
            daemon.start();
            exit(0);
        }

        else if(param == "stop")
        {
            daemon.stop();
            exit(0);
        }

        else if(param == "restart")
        {
            daemon.stop();
            daemon.start();
            exit(0);
        }

        else
        {
            cout << "param is invalid" << endl;
            cout << "usage: ./[program_name] start|stop|restart" << endl;
            exit(0);
        }
    }

    cout << "usage: ./[program_name] start|stop|restart" << endl;
    exit(0);
}

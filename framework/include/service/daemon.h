#ifndef DAEMON_H
#define DAEMON_H

#include <memory>
#include <service/service_proxy.h>

using namespace std;

namespace zhicloud{
    namespace service{
        class Daemon
        {
            public:
                Daemon(ServiceProxy* p);
                virtual ~Daemon();
                void start();
                void stop();
            private:
                void daemonize();
                void mainProcess();
                void console(const string& content);
                static void onSignal(int sig);
                unique_ptr< ServiceProxy > p_proxy;
        };
    }

}


#endif // DAEMON_H

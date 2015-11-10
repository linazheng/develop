#ifndef SYSTEM_STATUS_HPP
#define SYSTEM_STATUS_HPP

#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{
        class SystemStatus{
        public:
            SystemStatus():_memory_usage(0.0),_disk_usage(0.0)
            {
            }
        private:
            StatusCounter _server;
            StatusCounter _host;
            BaseCounter _counter;
            float _memory_usage;
            float _disk_usage;

        };
    }
}
#endif // SYSTEM_STATUS_HPP

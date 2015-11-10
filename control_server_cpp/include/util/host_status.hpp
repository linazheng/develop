#ifndef HOST_STATUS_HPP
#define HOST_STATUS_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class HostIp
        {
        public:
            HostIp()
            {
            }
        private:
            string _target_ip;
            string _public_ip;
        };
        class HostStatus{
        public:
            HostStatus():_memory_usage(0.0),_disk_usage(0.0)
            {

            }
        private:
            BaseCounter _counter;
            float _memory_usage;
            float _disk_usage;
            UUID_TYPE _server_uuid;//##server uuid
            UUID_TYPE _uuid;
            HostIp _ip;//##[target_ip, public_ip]
        };
    }

}


#endif // HOST_STATUS_HPP

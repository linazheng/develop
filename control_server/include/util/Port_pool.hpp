#ifndef PORT_POOL_HPP
#define PORT_POOL_HPP

#include "Util.hpp"


namespace zhicloud
{
    namespace control_server{

        class PortResource{
        public:
            PortResource():default_begin_port(1024),default_end_port(65535),_begin_port(default_begin_port),_end_port(default_end_port),
                _last_offset(0),_count(_end_port-_begin_port),_modify(true)
            {

            }

        private:
            const uint32_t default_begin_port;
            const uint32_t default_end_port;
            string _ip;
            uint32_t _begin_port;
            uint32_t _end_port;
            uint32_t _last_offset;
            uint32_t _count;
            set<uint32_t> _allocated;
            bool _modify;
        };

        class PortPool{
        public:
            PortPool():_enable(true),_modify(true)
            {
            }
        private:
            BaseSelfInfo _self;
            bool _enable;
            bool _modify;
            map<string,PortResource> _resource;//##key = ip, value = PortResource
        };
    }
}

#endif // PORT_POOL_HPP

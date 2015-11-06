#ifndef NETWORK_INFO_HPP
#define NETWORK_INFO_HPP

#include "Util.hpp"

namespace zhicloud
{
    namespace control_server{

         enum class NetworkStatusEnum:uint32_t
        {
            disabled = 0,
            enabled = 1,
        };


        class NetworkInfo{
        public:
            NetworkInfo():_size(0),_netmask(0),_status(NetworkStatusEnum::disabled)
            {
            }
        private:
            BaseSelfInfo _self;
            uint32_t _size;
            string _description;
            string _pool;
            string _network_address;
            uint32_t _netmask;
            string _broadcast_address;
            NetworkStatusEnum _status;
            set<UUID_TYPE> _hosts;//containing host UUIDs
            set<string> _public_ip;//containing public ip
            set<string> _allocated_ip;//containing allocated (inner vpc)ips
            map<string,string> _bound_ports;//# key: "protocol:public_ip:public_port", value: "host_uuid:host_port"

        };
    }
}

#endif // NETWORK_INFO_HPP

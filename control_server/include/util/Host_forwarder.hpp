#ifndef HOST_FORWARDER_HPP
#define HOST_FORWARDER_HPP

#include "Util.hpp"

namespace zhicloud
{
    namespace control_server{

        enum class ForwarderTypeEnum:uint32_t
        {
            mono = 0,
            share = 1,
            domain = 2,
            vpc = 3,

        };

        class PortRange{
        public:
            PortRange():_min_port(0),_max_port(0)
            {
            }
        private:
            uint32_t _min_port;
            uint32_t _max_port;
        };

        class ForwarderPort{
        public:
            ForwarderPort():_protocol(0),_server_port(0),_host_port(0),_public_port(0)
            {
            }
        private:
            uint32_t _protocol;
            uint16_t _server_port;
            uint16_t _host_port;
            string _public_ip;
            uint16_t _public_port;
        };

        class HostForwarder{
        public:
            HostForwarder():_type(ForwarderTypeEnum::mono),_public_monitor(0),_server_monitor(0),_enable(OptionStatusEnum::enabled),_crc(0)
            {
            }
        private:
            UUID_TYPE _uuid;
            ForwarderTypeEnum _type;
            string _host_id;
            string _host_name;
            vector<string> _public_ip;
            uint32_t _public_monitor;
            string _server_ip;
            uint32_t _server_monitor;
            string _vpc_ip;
            string _vpc_range;
            PortRange _output_port_range;//# [min_port, max_port]
            vector<ForwarderPort> _port;
            OptionStatusEnum _enable;
            uint32_t _crc;
        };
    }
}

#endif // HOST_FORWARDER_HPP

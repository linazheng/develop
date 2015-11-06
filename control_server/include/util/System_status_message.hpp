#ifndef SYSTEM_STATUS_MESSAGE_HPP_INCLUDED
#define SYSTEM_STATUS_MESSAGE_HPP_INCLUDED

#include <transport/app_message.h>
#include "Status_info.hpp"

namespace zhicloud
{
    namespace control_server{
        class SystemStatusMessage
        {
        public:
            SystemStatusMessage():_physical_node(0),_total_physical_node(0),_virtual_node(0),_total_virtual_node(0),
                    _network(0),_total_network(0),_total_cpu_usage(0.0),_memory_usage(0.0),_disk_usage(0.0),
                    _read_bytes(0),_io_error(0),_write_bytes(0)
            {

            }
            void toMessage(transport::AppMessage& request)
            {
            }

            void fromMessage(const transport::AppMessage& request)
            {

            }
        private:
            uint32_t _physical_node;
            uint64_t _total_physical_node;
            uint32_t _virtual_node;
            uint64_t _total_virtual_node;
            uint32_t _network;
            uint32_t _total_network;
            float _total_cpu_usage;
            float _memory_usage;
            float _disk_usage;
            uint64_t _read_bytes;
            uint32_t _io_error;
            uint64_t _write_bytes;
            TrafficCounter _received;
            TrafficCounter _send;
            string timestamp;

        };
    }
}

#endif // SYSTEM_STATUS_MESSAGE_HPP_INCLUDED

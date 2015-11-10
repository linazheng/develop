#ifndef STATUS_INFO_HPP_INCLUDED
#define STATUS_INFO_HPP_INCLUDED

#include "util.hpp"

namespace zhicloud
{
    namespace control_server{

        class CpuCounter{
        public:
            CpuCounter():_cpu_count(0),_cpu_usage(0.0)
            {
            }
        private:
            uint32_t _cpu_count;
            float _cpu_usage;
        };

        class StatusCounter
        {
        public:
            StatusCounter():_stop(0),_warning(0),_error(0),_running(0)
            {
            }
        private:
            uint32_t _stop;
            uint32_t _warning;
            uint32_t _error;
            uint32_t _running;
        };

        class ResourceCounter
        {
        public:
            ResourceCounter():_available(0),_total(0)
            {

            }
        private:
            uint64_t _available;
            uint64_t _total;
        };


        class DiskCounter
        {
        public:
            DiskCounter():_read_count(0),_read_bytes(0),_write_count(0),_write_bytes(0),_io_error(0)
            {

            }
        private:
            uint64_t _read_count;
            uint64_t _read_bytes;
            uint64_t _write_count;
            uint64_t _write_bytes;
            uint64_t _io_error;
        };

        class TrafficCounter
        {
        public:
            TrafficCounter():_traffic_bytes(0),_traffic_packets(0),_traffic_error(0),_traffic_drop(0)
            {
            }
        private:
            uint64_t _traffic_bytes;
            uint64_t _traffic_packets;
            uint64_t _traffic_error;
            uint64_t _traffic_drop;
        };

        class NetCounter
        {
        public:
            NetCounter()
            {
            }
        private:
            TrafficCounter _receive;
            TrafficCounter _send;
        };

        class DiskSpeedCounter
        {
        public:
            DiskSpeedCounter():_read(0),_write(0),_receive(0),_send(0)
            {
            }
        private:
            uint64_t _read;
            uint64_t _write;
            uint64_t _receive;
            uint64_t _send;
        };

        class BaseCounter{
        public:
            BaseCounter():_status(UnitStatusEnum::status_running)
            {
            }
        private:
            CpuCounter _cpu;
            ResourceCounter _memory;// ##[available, total]
            ResourceCounter _disk;// ##[available, total]
            DiskCounter _disk_io;//read_count, read_bytes, write_count, write_bytes, io_error
            TrafficCounter network_io;//##receive_bytes, receive_packets, receive_error, receive_drop,send_bytes, send_packets, send_error, send_drop
            DiskSpeedCounter _speed;
            string _timestamp;
            UnitStatusEnum _status;
        };
    }
}

#endif // STATUS_INFO_HPP_INCLUDED

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

            void setCpuCount(const uint32_t& value ){ _cpu_count = value;}
            void setCpuUsage(const float& value ){ _cpu_usage = value;}

            const uint32_t& getCpuCount() const { return _cpu_count;}
            const float& getCpuUsage() const { return _cpu_usage;}

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


            void IncreaseStop() { _stop += 1;}
            void IncreaseWarn() { _warning += 1;}
            void IncreaseError() { _error += 1;}
            void IncreaseRun() { _running += 1;}

            void DecreaseStop() { _stop -= 1;}
            void DecreaseWarn() { _warning -= 1;}
            void DecreaseError() { _error -= 1;}
            void DecreaseRun() { _running -= 1;}


            void transfertoArray(vector<uint64_t>& value) const
            {
                value.clear();
                value.emplace_back(_stop);
                value.emplace_back(_warning);
                value.emplace_back(_error);
                value.emplace_back(_running);
            }

        private:
            uint64_t _stop;
            uint64_t _warning;
            uint64_t _error;
            uint64_t _running;
        };

        class ResourceCounter
        {
        public:
            ResourceCounter():_available(0),_total(0)
            {

            }

            void transfertoArray(vector<uint64_t>& value) const
            {
                value.clear();
                value.emplace_back(_available);
                value.emplace_back(_total);
            }

            void setAvailable(const uint64_t& value ){ _available = value;}
            void setTotal(const uint64_t& value ){ _total = value;}

            const uint64_t& getAvailable() const { return _available;}
            const uint64_t& getTotal() const { return _total;}

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

            void transfertoArray(vector<uint64_t>& value) const
            {
                value.clear();
                value.emplace_back(_read_count);
                value.emplace_back(_read_bytes);
                value.emplace_back(_write_count);
                value.emplace_back(_write_bytes);
                value.emplace_back(_io_error);
            }

            const uint64_t& getReadCount()const {return _read_count; }
            const uint64_t& getReadBytes()const {return _read_bytes; }
            const uint64_t& getWriteCount()const {return _write_count; }
            const uint64_t& getWriteBytes()const {return _write_bytes; }
            const uint64_t& getIOError()const {return _io_error; }

            void setReadCount(const uint64_t& value) {  _read_count = value;}
            void setReadBytes(const uint64_t& value) {  _read_bytes=value; }
            void setWriteCount(const uint64_t& value) {  _write_count=value; }
            void setWriteBytes(const uint64_t& value)  {  _write_bytes=value; }
            void SetIOError(const uint64_t& value)  {  _io_error=value; }



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

            void transfertoArray(vector<uint64_t>& value) const
            {
                value.clear();
                value.emplace_back(_traffic_bytes);
                value.emplace_back(_traffic_packets);
                value.emplace_back(_traffic_error);
                value.emplace_back(_traffic_drop);
            }

            const uint64_t& getByte()const { return _traffic_bytes;}
            const uint64_t& getPacket()const { return _traffic_packets;}
            const uint64_t& getError()const { return _traffic_error;}
            const uint64_t& getDrop()const { return _traffic_drop;}

            void setByte(const uint64_t& value) {  _traffic_bytes = value;}
            void setPacket(const uint64_t& value) {  _traffic_packets = value;}
            void setError(const uint64_t& value) {  _traffic_error = value;}
            void setDrop(const uint64_t& value) {  _traffic_drop = value;}

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
            const TrafficCounter& getReceive()const { return _receive;}
             const TrafficCounter& getSend()const { return _send;}

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

            void transfertoArray(vector<uint64_t>& value) const
            {
                value.clear();
                value.emplace_back(_read);
                value.emplace_back(_write);
                value.emplace_back(_receive);
                value.emplace_back(_send);
            }
            
            const uint64_t& getRead()const { return _read;}
            const uint64_t& getWrite()const { return _write;}
            const uint64_t& getReceive()const { return _receive;}
            const uint64_t& getSend()const { return _send;}

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

            const CpuCounter& getCpuCounter()const { return _cpu; }
            const ResourceCounter& getMemoryCounter()const { return _memory; }
            const ResourceCounter& getDiskCounter()const { return _disk; }
            const DiskCounter& getDiskIOCounter()const { return _disk_io; }
            const TrafficCounter& getNetworkCounter()const { return network_io; }
            const DiskSpeedCounter& getSpeedCounter()const { return _speed; }
            const UnitStatusEnum& getStatus()const { return _status; }

            void setCpuCounter(const CpuCounter& value) {  _cpu = value; }
            void setMemoryCounter(const ResourceCounter& value) { _memory = value; }
            void setDiskCounter(const ResourceCounter& value) {  _disk = value; }
            void setDiskIOCounter(const DiskCounter& value) {  _disk_io = value; }
            void setNetworkCounter(const TrafficCounter& value) {  network_io = value; }
            void setSpeedCounter(const DiskSpeedCounter& value) {  _speed = value; }
            void setStatus(const UnitStatusEnum& value) {  _status = value; }


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

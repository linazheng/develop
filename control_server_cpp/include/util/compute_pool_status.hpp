#ifndef COMPUTE_POOL_STATUS_HPP
#define COMPUTE_POOL_STATUS_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{


        class ComputePoolStatus{
        public:
            ComputePoolStatus():_memory_usage(0.0),_disk_usage(0.0),_status(UnitStatusEnum::status_stop)
            {

            }

            ComputePoolStatus& operator=(const ComputePoolStatus& other)
            {

                copy(other);
                return *this;
            }

            ComputePoolStatus(const ComputePoolStatus& other)
            {
                 copy(other);
            }

            void setName(const string& value){ _self.setName(value); }
            void setUUID(const UUID_TYPE& value){ _self.setUUID(value); }
            void setStatus(const UnitStatusEnum& value){ _status = value; }
            void setCpuCounter(const CpuCounter& value){ _cpu = value; }
            void setNodeStatus(const StatusCounter& value){ _node_status = value; }
            void setHostStatus(const StatusCounter& value){ _host_status = value; }
            void setMemory(const ResourceCounter& value){ _memory = value; }
            void setDisk(const ResourceCounter& value){ _disk_volume = value; }
            void setMemoryUsage(const float& value){ _memory_usage = value;}
            void setDiskUsage(const float& value){ _disk_usage = value;}


            const UUID_TYPE& getName()const { return  _self.getName(); }
            const UUID_TYPE& getUUID()const { return  _self.getUuid(); }
            const UnitStatusEnum& getStatus() const { return _status; }
            const CpuCounter& getCpuCounter() const { return _cpu;}
            const ResourceCounter& getMemory() const { return _memory;}
            const ResourceCounter& getDisk() const { return _disk_volume;}
            const StatusCounter& getHost() const { return _host_status;}
            const float& getMemoryUsage() const { return _memory_usage;}
            const float& getDiskUsage() const { return _disk_usage;}


        private:

            void copy(const ComputePoolStatus& other)
            {
                _self = other._self;
                _node_status = other._node_status;
                _host_status = other._host_status;
                _cpu = other._cpu;
                _memory = other._memory;
                _memory_usage = other._memory_usage;
                _disk_volume = other._disk_volume;
                _status = other._status;
                _timestamp = other._timestamp;
            }

            BaseSelfInfo _self;
            StatusCounter _node_status;//##[stop, warning, error, running]
            StatusCounter _host_status;//##[stop, warning, error, running]
            CpuCounter _cpu;
            ResourceCounter _memory;//##[available, total]
            float _memory_usage;
            ResourceCounter _disk_volume;//##[available, total]
            float _disk_usage;
            UnitStatusEnum _status;
            string _timestamp;

        };
    }
}

#endif // COMPUTE_POOL_STATUS_HPP

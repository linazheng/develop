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

        private:
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

#ifndef SNAPSHOT_POOL_HPP
#define SNAPSHOT_POOL_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class SnapshotNode{
        public:
            SnapshotNode():_status(0),_memory_usage(0.0),_disk_usage(0.0)
            {
            }
        private:
            string _name;
            uint32_t _status;
            CpuCounter _cpu;
            ResourceCounter _memory;
            ResourceCounter _disk;
            float _memory_usage;
            float _disk_usage;
        };

        class SnapshotPool{
        public:
            SnapshotPool():_memory_usage(0),_disk_usage(0),_status(0)
            {
            }
        private:
            BaseSelfInfo _self;
            string _data_index;
            StatusCounter _node;
            ResourceCounter _snapshot;
            ResourceCounter _memory;
            ResourceCounter _disk;
            CpuCounter _cpu;
            float _memory_usage;
            float _disk_usage;
            uint32_t _status;
            vector<SnapshotNode> _snapshot_node_list;
        };
    }
}

#endif // SNAPSHOT_POOL_HPP

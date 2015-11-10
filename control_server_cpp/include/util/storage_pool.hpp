#ifndef STORAGE_POOL_HPP
#define STORAGE_POOL_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        enum class FileSystemFormatEnum:uint32_t
        {
            raw = 0,
            ext3 = 1,
            ntfs = 2,
            ext4 = 3,
        };

        class Device{
        public:
            Device():_level(0),_security(0),_crypt(0),_page(0)
            {
            }
        private:
            string _storage_pool;
            BaseSelfInfo _self;
            uint32_t _level;
            string _identity;
            uint32_t _security;
            uint32_t _crypt;
            uint32_t _page;
            vector<uint32_t> _disk_volume;
        };

        class StorageResource{
        public:
            StorageResource():_status(0)
            {
            }
        private:
            string _storage_pool;
            string _name;
            uint32_t _status;
            CpuCounter _cpu;
            ResourceCounter _memory;
            ResourceCounter _disk;
            string _ip;
        };

        class StoragePool{
        public:
            StoragePool():_status(0)
            {
            }
        private:
            BaseSelfInfo _self;
            string _data_index;
            StatusCounter _node;
            CpuCounter _cpu;
            ResourceCounter _memory;
            ResourceCounter _disk;
            uint32_t _status;
        };
    }
}

#endif // STORAGE_POOL_HPP

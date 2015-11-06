#ifndef DISK_IMAGE_HPP
#define DISK_IMAGE_HPP

#include "Util.hpp"
#include "Compute_pool.hpp"

using namespace std;

namespace zhicloud
{
    namespace control_server{

        enum class DiskImageFileTypeEnum:uint32_t
        {
            raw = 0,
            qcow2 = 1,
        };

        class DiskImage{
        public:
            DiskImage():_size(0),_disk_type(ComputeStorageTypeEnum::local),_file_type(DiskImageFileTypeEnum::raw)
            {
            }
        private:
            BaseSelfInfo _self;
            bool _enable;
            uint32_t _size;
            vector<string> _tag;
            string _description;
            string _group;
            string _user;
            string _path;
            ComputeStorageTypeEnum _disk_type;
            DiskImageFileTypeEnum _file_type;
            string _container;

        };
    }
}

#endif // DISK_IMAGE_HPP

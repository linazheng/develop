#ifndef ISO_IMAGE_HPP
#define ISO_IMAGE_HPP

#include "Util.hpp"
#include "Compute_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class ISOImage{
        public:
            ISOImage():_enable(OptionStatusEnum::enabled),_size(0),_port(0),_disk_type(ComputeStorageTypeEnum::local)
            {
            }
        private:
            BaseSelfInfo _self;
            OptionStatusEnum _enable;
            uint32_t _size;
            string _description;
            string _ip;
            uint32_t _port;
            string _group;
            string _user;
            string _path;//nas path
            ComputeStorageTypeEnum _disk_type;
            string _container;//storage service name
        };
    }
}
#endif // ISO_IMAGE_HPP

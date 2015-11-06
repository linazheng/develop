#ifndef COMPUTE_POOL_HPP
#define COMPUTE_POOL_HPP

#include "Util.hpp"

namespace zhicloud
{
    namespace control_server{

        class ComputeResource{
        public:
            ComputeResource():_status(0)
            {
            }

        private:
            string _name;//service name
            UUID_TYPE _server_uuid;
            uint32_t _status;
            set<string> _allocated_hostid;
        };

        enum class ComputeStorageTypeEnum:uint32_t
        {
            local = 0,
            cloud = 1,
            nas = 2,
            ip_san = 3,
        };

        enum class ComputeNetworkTypeEnum:uint32_t
        {
            privates = 0,
            monopoly = 1,
            share = 2,
            bridge = 3,
        };

        typedef OptionStatusEnum HighAvaliableModeEnum;
        typedef OptionStatusEnum AutoQOSModeEnum;
        typedef OptionStatusEnum ThinProvisioningModeEnum;
        typedef OptionStatusEnum BackingImageModeEnum;


        class ComputePool{
        public:
            ComputePool():_status(0),_network_type(ComputeNetworkTypeEnum::privates),
                _disk_type(ComputeStorageTypeEnum::local),_high_available(HighAvaliableModeEnum::disabled),
                _auto_qos(AutoQOSModeEnum::disabled),_thin_provisioning(ThinProvisioningModeEnum::disabled),
                _backing_image(BackingImageModeEnum::disabled)
            {


            }

        private:
            BaseSelfInfo _self;
            uint32_t _status;
            UUID_TYPE _network_uuid;//##network pool uuid
            UUID_TYPE _disk_uuid;//uuid for storage pool, when using cloud storage
            string _path;
            string _crypt;
            map<string,ComputeResource> _resource;//key = name, value = compute resource

            ComputeNetworkTypeEnum _network_type;
            ComputeStorageTypeEnum _disk_type;
            HighAvaliableModeEnum _high_available;
            AutoQOSModeEnum _auto_qos;
            ThinProvisioningModeEnum _thin_provisioning;
            BackingImageModeEnum _backing_image;
        };

    }
}

#endif // COMPUTE_POOL_HPP_INCLUDED

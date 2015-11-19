#ifndef COMPUTE_POOL_HPP
#define COMPUTE_POOL_HPP

#include "util.hpp"

namespace zhicloud
{
    namespace control_server{

        class ComputeResource{
        public:
            ComputeResource():_status(OptionStatusEnum::disabled)
            {
            }

            ComputeResource& operator=(const ComputeResource& other)
            {
                copy(other);

                return *this;
            }

            ComputeResource(const ComputeResource& other)
            {
                copy(other);
            }

            bool containsHost(const UUID_TYPE &uuid)
            {
                return ((_allocated_hostid.count(uuid) == 1) ? true:false);
            }

            void removeHost(const UUID_TYPE &uuid)
            {
                set<UUID_TYPE>::iterator iter = _allocated_hostid.find(uuid);
                if(iter != _allocated_hostid.end())
                    _allocated_hostid.erase(iter);
            }

            bool addHost(const UUID_TYPE &uuid)
             {
                if( 0 == _allocated_hostid.count(uuid)){
                    _allocated_hostid.emplace(uuid);
                    return true;
                 }

                return false;
             }

            void setName(const string& value) {_name = value;}
            void setUUID(const string& value) {_server_uuid = value;}
            void setStatus(const OptionStatusEnum& value) {_status = value;}
            void setHost(const UUID_TYPE& value) {  _allocated_hostid.emplace(value); }

            const string& getName() const { return _name;}
            const UUID_TYPE& getServerUUID() const {return _server_uuid;}
            const OptionStatusEnum& getStatus() const {return _status;}
            const set<UUID_TYPE>& getHostList() const {return _allocated_hostid;}
            const uint32_t getHostSize() const { return _allocated_hostid.size(); }

        private:
            void copy(const ComputeResource& other)
            {
                _allocated_hostid.clear();
                _name  = other._name;
                _server_uuid = other._server_uuid;
                _status = other._status;

                for(const auto& item: other._allocated_hostid)
                    _allocated_hostid.emplace(item);
            }


            string _name;//service name
            UUID_TYPE _server_uuid;
            OptionStatusEnum _status;
            set<UUID_TYPE> _allocated_hostid;
        };

        enum class ComputeNetworkTypeEnum:uint32_t
        {
            privates = 0,
            monopoly = 1,
            share = 2,
            bridge = 3,
        };

        typedef StorageTypeEnum ComputeStorageTypeEnum;
        typedef OptionStatusEnum HighAvaliableModeEnum;
        typedef OptionStatusEnum AutoQOSModeEnum;
        typedef OptionStatusEnum ThinProvisioningModeEnum;
        typedef OptionStatusEnum BackingImageModeEnum;


        class ComputePool{
        public:
            ComputePool():_status(OptionStatusEnum::disabled),_network_type(ComputeNetworkTypeEnum::privates),
                _disk_type(ComputeStorageTypeEnum::local),_high_available(HighAvaliableModeEnum::disabled),
                _auto_qos(AutoQOSModeEnum::disabled),_thin_provisioning(ThinProvisioningModeEnum::disabled),
                _backing_image(BackingImageModeEnum::disabled)
            {


            }

            ComputePool& operator=(const ComputePool& other)
            {

                copy(other);
                return *this;
            }

            ComputePool(const ComputePool& other)
            {
                 copy(other);
            }

            bool isEmpty()
            {
                return ((_resource.size() == 0 )? true:false);
            }

            void setName(const string& value){ _self.setName(value); }
            void setUUID(const UUID_TYPE& value){ _self.setUUID(value); }
            void setNetwork(const string& value){ _network_uuid = value;}
            void setDisk(const string& value){ _disk_uuid = value; }
            void setPath(const string& value){ _path = value; }
            void setCrypt(const string& value){ _crypt = value; }
            void setStatus(const OptionStatusEnum& value){ _status = value; }
            void setNetworkType(const ComputeNetworkTypeEnum& value){ _network_type = value; }
            void setStorageType(const ComputeStorageTypeEnum& value){ _disk_type = value; }
            void setHighAvaliableMode(const HighAvaliableModeEnum& value){ _high_available = value; }
            void setAutoQOSMode(const AutoQOSModeEnum& value){ _auto_qos = value; }
            void setThinProvisioningMode(const ThinProvisioningModeEnum& value){ _thin_provisioning = value; }
            void setBackingImageMode(const BackingImageModeEnum& value){ _backing_image = value; }

            bool setResource(const string& name,const ComputeResource &value)
            {   if(_resource.count(name) == 0)
                {
                    _resource.emplace(name,value);
                    return true;
                }
                return false;
            }


            const UUID_TYPE& getName()const { return  _self.getName(); }
            const UUID_TYPE& getUUID()const { return  _self.getUuid(); }
            const UUID_TYPE& getNetWork()const { return _network_uuid; }
            const UUID_TYPE& getDisk()const { return _disk_uuid; }
            const string& getPath()const { return _path; }
            const string& getCrypt()const { return _crypt; }
            const OptionStatusEnum& getStatus()const { return _status; }
            const ComputeNetworkTypeEnum& getNetWorkType()const { return _network_type; }
            const ComputeStorageTypeEnum& getStorageType()const { return _disk_type; }
            const HighAvaliableModeEnum& getHighAvaliableMode()const { return _high_available; }
            const AutoQOSModeEnum& getAutoQOSMode()const { return _auto_qos; }
            const ThinProvisioningModeEnum& getThinProvisioningMode()const { return _thin_provisioning; }
            const BackingImageModeEnum& getBackingImageMode()const { return _backing_image; }

            bool containResource(const string& name)const { return (_resource.count(name) == 1 ? true:false); }

            const map<string,ComputeResource> &getResourceList()const { return _resource;}

            bool removeResource(const string& name)
            {
                auto iter =_resource.find(name);
                if( iter !=  _resource.end()){
                    _resource.erase(iter);
                    return true;
                }

                return false;
            }



        private:
            void copy(const ComputePool& other)
            {
                _resource.clear();
                _self  = other._self;
                _status = other._status;
                _network_uuid = other._network_uuid;
                _disk_uuid = other._disk_uuid;
                _path = other._path;
                _crypt = other._crypt;
                _network_type = other._network_type;
                _disk_type = other._disk_type;
                _high_available = other._high_available;
                _auto_qos = other._auto_qos;
                _thin_provisioning = other._thin_provisioning;
                _backing_image = other._backing_image;


                for(const auto& item: other._resource)
                    _resource.emplace(item);
            }

            BaseSelfInfo _self;
            OptionStatusEnum _status;
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

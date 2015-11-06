#ifndef STORAGEMANAGER_H
#define STORAGEMANAGER_H

#include <util/logging.h>


#include "Storage_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class StorageManager
        {
        public:
            StorageManager(const string& logger_name);
            ~StorageManager();

        protected:
            StorageManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;

            map<UUID_TYPE,StoragePool> _storage_pool_info;// storage_pool_uuid : StoragePool instance,
            mutable recursive_mutex _storage_pool_mutex;

            map<UUID_TYPE,StorageResource> _storage_resource_info;//resource_name : StorageResource instance,
            mutable recursive_mutex _storage_resource_mutex;

            map<UUID_TYPE,Device> _device_info;//device_uuid : Device instance,
            mutable recursive_mutex _device_info_mutex;

            util::logger_type _logger;
        };
}
}

#endif // STORAGEMANAGER_H

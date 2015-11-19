#ifndef COMPUTEPOOLMANAGER_H
#define COMPUTEPOOLMANAGER_H

#include <util/logging.h>
#include "compute_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class ComputePoolManager
        {
        public:
            ComputePoolManager(const string& resource_path,const string& logger_name);
            ~ComputePoolManager();

            bool load();

            bool savePoolList();
            bool savePoolInfo(const UUID_TYPE& pool_id);
            bool savePoolResource(const UUID_TYPE& pool_id,const UUID_TYPE& resource_name);
            void deleteResourceFile(const UUID_TYPE& pool_id,const UUID_TYPE& resource_name);
            void deletePoolPath(const UUID_TYPE& pool_id);
            void getDefaultPoolID(string &pool_id) const;
            bool getDefaultPool(ComputePool &pool) const;
            void queryAllPool(map<UUID_TYPE,ComputePool> &compute_pool) const;

            bool createPool(ComputePool &pool);
            bool modifyPool(const ComputePool &pool);
            bool deletePool(const UUID_TYPE& pool_id);
            bool containsPool(const UUID_TYPE& pool_id) const;
            bool getPool(const UUID_TYPE& pool_id, ComputePool &pool) const;

            bool addResource(const UUID_TYPE& pool_id,vector<ComputeResource>& resource_list);
            bool removeResource(const UUID_TYPE& pool_id,const vector<string>& name_list);
            void queryResource(const UUID_TYPE& pool_id,vector<ComputeResource>& resource_list) const;
            bool searchResource(const string& name,UUID_TYPE& uuid);
            bool containsResource(const UUID_TYPE& pool_id,const string& name);
            bool getResource(const UUID_TYPE& pool_id,const string& name,ComputeResource &resource) const;
            bool containNetwork(const UUID_TYPE& network);

        protected:
            ComputePoolManager(){}
            bool loadAllPool();

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            UUID_TYPE _default_pool;
            string _pool_path;
            string _pool_config;
            map<UUID_TYPE,ComputePool> _compute_pool;
        };
    }
}

#endif // COMPUTEPOOLMANAGER_H

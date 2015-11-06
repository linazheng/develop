#ifndef COMPUTEPOOLMANAGER_H
#define COMPUTEPOOLMANAGER_H

#include <util/logging.h>
#include "Compute_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class ComputePoolManager
        {
        public:
            ComputePoolManager(const string& resource_path,const string& logger_name);
            ~ComputePoolManager();

        protected:
            ComputePoolManager(){}

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            string _default_pool;
            map<UUID_TYPE,ComputePool> _compute_pool;
        };
    }
}

#endif // COMPUTEPOOLMANAGER_H

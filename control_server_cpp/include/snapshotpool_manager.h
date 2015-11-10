#ifndef SNAPSHOTPOOLMANAGER_H
#define SNAPSHOTPOOLMANAGER_H


#include <util/logging.h>
#include "snapshot_pool.hpp"

namespace zhicloud
{
    namespace control_server{

    class SnapshotPoolManager
    {
        public:
            SnapshotPoolManager(const string& logger_name);
            ~SnapshotPoolManager();

        protected:
            SnapshotPoolManager();
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            vector<SnapshotPool> _snapshot_pool_info;
        };
    }
}

#endif // SNAPSHOTPOOLMANAGER_H

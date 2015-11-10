#ifndef MONITORMANAGER_H
#define MONITORMANAGER_H

#include <util/logging.h>
#include "monitor_task.hpp"

namespace zhicloud
{
    namespace control_server{

        class MonitorManager
        {
        public:
            MonitorManager(const string& logger_name);
            ~MonitorManager();

        protected:
            MonitorManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            uint32_t _task_id_seed;
            map<uint32_t,MonitorTask> _task_map;//##key = task id, value = task
            const static uint32_t _max_timeout;
        };
    }
}
#endif // MONITORMANAGER_H

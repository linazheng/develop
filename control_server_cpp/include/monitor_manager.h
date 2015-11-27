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

            bool addTask(MonitorTask& task);
            bool getTask(const uint32_t& task_id, MonitorTask& task);
            void processHeartBeat(const uint32_t& task_id);
            void checkTimeout();
            void getAllMonitor( vector<Monitor>& monitor_list);
            bool removeTask(const uint32_t& task_id);

        protected:
            MonitorManager(){}


            bool isNodeMonitored(const string& node_name){ return true;}
            bool getNodeMonitor(const string& node_name,Monitor& value){ return true;}
            bool isDomainMonitored(const string& node_name){ return true;}
            bool getDomainMonitor(const string& node_name,Monitor& value){ return true;}

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            uint32_t _task_id_seed;
            map<uint32_t,MonitorTask> _task_map;//##key = task id, value = task
            const static uint32_t _max_timeout;
            vector<Monitor> _monitor_list;
        };
    }
}
#endif // MONITORMANAGER_H

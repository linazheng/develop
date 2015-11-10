#ifndef MONITORTASK_HPP
#define MONITORTASK_HPP

#include "util.hpp"


namespace zhicloud
{
    namespace control_server{

        class Monitor{
        public:
            Monitor()
            {
            }
        private:
            MonitorLevelEnum _level;
            vector<uint32_t>_listener_list;//task id
            vector<uint32_t>_global_listener; //task id
            map<string,vector<uint32_t>> _target_map;//##key = target id, value = list of task id
        };

        class MonitorTask{
        public:
            MonitorTask():_task_id(0),_receive_session(0),_monitor_level(0),_global_monitor(false),_timeout_count(0)
            {
            }

        private:
            uint32_t _task_id;
            string _receive_node;
            uint32_t _receive_session;
            uint32_t _monitor_level;
            bool _global_monitor;
            uint32_t _timeout_count;
            vector<string> _target_lists;
        };

    }
}

#endif // MONITORTASK_HPP

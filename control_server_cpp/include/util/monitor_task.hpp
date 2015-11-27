#ifndef MONITORTASK_HPP
#define MONITORTASK_HPP

#include "util.hpp"


namespace zhicloud
{
    namespace control_server{

        class Monitor{
        public:
            Monitor(const MonitorLevelEnum& level):_level(level)
            {
            }

            Monitor& operator=(const Monitor& other)
            {

                copy(other);
                return *this;
            }

            Monitor(const Monitor& other)
            {
                 copy(other);
            }

            void addGlobalListener(const uint32_t& task_id)
            {
                _global_listener.emplace(task_id);
            }

            void removeGlobalListener(const uint32_t& task_id)
            {
                auto iter = _global_listener.find(task_id);
                if(iter != _global_listener.end())
                    _global_listener.erase(iter);
            }

            void addListener(const uint32_t& task_id)
            {
                _listener_list.emplace(task_id);
            }


            void removeListener(const uint32_t& task_id)
            {
                auto iter = _listener_list.find(task_id);
                if(iter != _listener_list.end())
                    _listener_list.erase(iter);
            }

            const MonitorLevelEnum& getLevel()const {return _level;}
            void setLevel(const MonitorLevelEnum& value) { _level = value;}

            void addTarget(const string& target_id,const uint32_t& task_id)
            {
                if(_target_map.count(target_id) == 0)
                    _target_map[target_id] = move(set<uint32_t>());

                 _target_map[target_id].emplace(task_id);
            }

            void removeTarget(const string& target_id,const uint32_t& task_id)
            {
                auto target = _target_map.find(target_id);
                if(target != _target_map.end())
                {
                    auto task = target->second.find(task_id);
                    if(task != target->second.end())
                        target->second.erase(task);

                    if(target->second.size() == 0)
                         _target_map.erase(target);
                }

            }

            bool hasTarget() { return (_target_map.size() > 0 ? true : false); }
            bool hasListener() { return (_listener_list.size() > 0 ? true : false); }
            const set<uint32_t>& getListener()const { return _listener_list; }
            const map<string,set<uint32_t>>& getTargetList()const {return _target_map;}

        private:

            void copy(const Monitor& other)
            {
                _level = other._level;
                _listener_list = other._listener_list;
                _global_listener = other._global_listener;
                _target_map = other._target_map;
            }
            MonitorLevelEnum _level;
            set<uint32_t>_listener_list;//task id
            set<uint32_t>_global_listener; //task id
            map<string,set<uint32_t>> _target_map;//##key = target id, value = list of task id
        };

        class MonitorTask{
        public:
            MonitorTask():_task_id(0),_receive_session(0),_monitor_level(MonitorLevelEnum::system),_global_monitor(false),_timeout_count(0)
            {
            }

            MonitorTask& operator=(const MonitorTask& other)
            {

                copy(other);
                return *this;
            }

            MonitorTask(const MonitorTask& other)
            {
                 copy(other);
            }

            const uint32_t& getTaskID()const {return _task_id;}
            const string& getReceivedNode()const {return _receive_node;}
            const uint32_t& getReceivedSession()const {return _receive_session;}
            const MonitorLevelEnum& getLevel()const {return _monitor_level;}
            const bool& getGlobalMonitor()const {return _global_monitor;}
            const uint32_t& getTimeOut()const {return _timeout_count;}

            void setTaskID(const uint32_t& value)  {_task_id = value;}
            void setReceivedNode(const string& value)  { _receive_node = value;}
            void setReceivedSession(const uint32_t& value) {_receive_session = value;}
            void setLevel(const MonitorLevelEnum& value) { _monitor_level = value;}
            void setGlobalMonitor(const bool& value) { _global_monitor = value;}
            void setTimeOut(const uint32_t& value) { _timeout_count = value;}
            void IncreaseTimeOut() { _timeout_count += 1;}

            const vector<string>& getTargetLists()const {return _target_lists;}
            void addTarget(const string& value) { _target_lists.emplace_back(value);}
            void addTargetList(const vector<string>& target_list) { _target_lists = target_list; }
            bool conatinTarget() {return (_target_lists.size() > 0 ? true:false);}
        private:

            void copy(const MonitorTask& other)
            {
                _task_id = other._task_id;
                _receive_node = other._receive_node;
                _receive_session = other._receive_session;
                _monitor_level = other._monitor_level;
                _timeout_count = other._timeout_count;
                _target_lists = other._target_lists;

            }
            uint32_t _task_id;
            string _receive_node;
            uint32_t _receive_session;
            MonitorLevelEnum _monitor_level;
            bool _global_monitor;
            uint32_t _timeout_count;
            vector<string> _target_lists;
        };

    }
}

#endif // MONITORTASK_HPP

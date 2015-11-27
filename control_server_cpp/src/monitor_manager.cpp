#include "monitor_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;
const uint32_t MonitorManager::_max_timeout(5);


MonitorManager::MonitorManager(const string& logger_name)
{
    _logger = getLogger(logger_name);

    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::system));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::server_room));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::server_rack));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::server));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::compute_node));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::storage_node));
    _monitor_list.emplace_back(Monitor(MonitorLevelEnum::host));
}

MonitorManager::~MonitorManager()
{
    //dtor

}

bool MonitorManager::addTask(MonitorTask& task)
{
    lock_type lock(_mutex);
    _task_id_seed +=1;
    task.setTaskID(_task_id_seed);

    for(auto& item :_monitor_list)
    {
        if(item.getLevel() == task.getLevel())
        {
            if(_task_map.count(task.getTaskID()) == 1)
            {
                _logger->error(boost::format("<MonitorManager> addTask  repeat task id %d") %task.getTaskID());
                 return false;
            }


            _task_map.emplace(task.getTaskID(),task);
            item.addListener(task.getTaskID());

            if(task.getGlobalMonitor()){
                item.addGlobalListener(task.getTaskID());
            }else{
                const vector<string>& targetlist = task.getTargetLists();
                for(const auto& target : targetlist)
                {
                    item.addTarget(target,task.getTaskID());
                }
            }
             _logger->info(boost::format("<MonitorManager> addTask task %d ok") %task.getTaskID());
            return true;
        }
    }
    _logger->error(boost::format("<MonitorManager> addTask  invalid monitor level task %d") %task.getTaskID());
    return false;
}

bool MonitorManager::getTask(const uint32_t& task_id,MonitorTask& task)
{
    lock_type lock(_mutex);
    auto item =_task_map.find(task_id);
    if(item != _task_map.end())
    {
        task = item->second;
        return false;
    }
    return false;
}

void MonitorManager::processHeartBeat(const uint32_t& task_id)
{
    lock_type lock(_mutex);
    auto item =_task_map.find(task_id);
    if(item != _task_map.end())
    {
        item->second.setTimeOut(0);

    }
}

void MonitorManager::checkTimeout()
{
    lock_type lock(_mutex);
    vector<uint32_t> task_list;

    for(auto& item :_task_map)
    {
        item.second.IncreaseTimeOut();
        if( item.second.getTimeOut() > _max_timeout)
        {
            task_list.emplace_back(item.second.getTaskID());
             _logger->info(boost::format("<MonitorManager> checkTimeout task %d time out") %item.second.getTaskID());
        }

    }

    for(const auto& task :task_list)
        removeTask(task);
}

bool MonitorManager::removeTask(const uint32_t& task_id)
{
     lock_type lock(_mutex);
     auto task_iter = _task_map.find(task_id);
     if( task_iter != _task_map.end())
     {
        MonitorTask& task = task_iter->second;
        for( auto& monitor : _monitor_list)
        {
            if(task.getLevel() == monitor.getLevel())
            {
                monitor.removeListener(task_id);
                if(task.getGlobalMonitor())
                {
                    monitor.removeGlobalListener(task_id);
                    _logger->info(boost::format("<MonitorManager> removeGlobalListener task %d") %task_id);
                }else{
                    const vector<string>& target_list = task.getTargetLists();
                    for(auto& target:target_list)
                    {
                       monitor.removeTarget(target,task_id);
                       _logger->info(boost::format("<MonitorManager> removeTask task %d") %task_id);
                    }
                }

            }
        }
        _task_map.erase(task_iter);
        _logger->info(boost::format("<MonitorManager> removeTask task %d ok") %task_id);
        return true;
     }
      _logger->error(boost::format("<MonitorManager> removeTask task %d invaild") %task_id);
     return false;
}

 void MonitorManager::getAllMonitor( vector<Monitor>& monitor_list)
 {
    lock_type lock(_mutex);
    for(const auto& item : _monitor_list)
        monitor_list.emplace_back(item);
 }

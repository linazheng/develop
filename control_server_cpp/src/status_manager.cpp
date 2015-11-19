#include "status_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

const uint32_t StatusManager::_max_timeout(24);

StatusManager::StatusManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

StatusManager::~StatusManager()
{
    //dtor
}

void StatusManager::checkTimeout()
{
    lock_type lock(_mutex);

    //server room
    auto room_iter  = _server_room_counter.begin();
    for( ;room_iter!= _server_room_counter.end(); )
    {
        room_iter->second +=1;
        if(room_iter->second >_max_timeout){
             _logger->info(boost::format("<StatusManager>server room status timeout, id '%s'") %room_iter->first);
            auto status_iter = _server_room_status.find(room_iter->first);
            if(status_iter != _server_room_status.end())
                     _server_room_status.erase(status_iter);

             _server_room_counter.erase(room_iter++);

         }else{
               room_iter++;
         }
    }

    //server rack
    auto rack_iter  = _server_rack_counter.begin();
    for( ;rack_iter!= _server_rack_counter.end(); )
    {
        rack_iter->second +=1;
        if(rack_iter->second >_max_timeout){
              _logger->info(boost::format("<StatusManager>server rack status timeout, id '%s'") %rack_iter->first);
             auto status_iter = _server_rack_status.find(rack_iter->first);
            if(status_iter != _server_rack_status.end())
                     _server_rack_status.erase(status_iter);

             _server_rack_counter.erase(rack_iter++);

         }else{
               rack_iter++;
         }
    }

     //server
    auto server_iter  =  _server_counter.begin();
    for( ;server_iter!= _server_counter.end(); )
    {
        server_iter->second +=1;
        if(server_iter->second >_max_timeout){
             _logger->info(boost::format("<StatusManager>server status timeout, id '%s'") %server_iter->first);
            auto status_iter = _server_status.find(server_iter->first);
            if(status_iter != _server_status.end())
                     _server_status.erase(status_iter);

             _server_counter.erase(server_iter++);

         }else{
               server_iter++;
         }
    }

   //host
    auto host_iter  =  _host_counter.begin();
    for( ;host_iter!= _host_counter.end(); )
    {
        host_iter->second +=1;
        if(host_iter->second >_max_timeout){
             _logger->info(boost::format("<StatusManager>host status timeout, id '%s'") %host_iter->first);
             auto status_iter = _host_status.find(host_iter->first);
            if(status_iter != _host_status.end())
                     _host_status.erase(status_iter);

             _host_counter.erase(host_iter++);

         }else{
               host_iter++;
         }
    }

    //compute pool
    auto compute_iter  = _compute_pool_counter.begin();
    for( ;compute_iter!= _compute_pool_counter.end(); )
    {
        compute_iter->second +=1;

        if(compute_iter->second >_max_timeout){
             _logger->info(boost::format("<StatusManager>compute pool status timeout, id '%s'") %compute_iter->first);
            auto status_iter = _compute_pool_status.find(compute_iter->first);
            if(status_iter != _compute_pool_status.end())
                     _compute_pool_status.erase(status_iter);

             _compute_pool_counter.erase(compute_iter++);

         }else{
               compute_iter++;
         }
    }

}

void StatusManager::updateServerStatus(const vector<ServerStatus>& value)
{
    lock_type lock(_mutex);

    for(auto & iter : value)
    {
        _server_status[iter.getUUID()] = iter;
        _server_counter[iter.getUUID()] = 0;
    }


}
void StatusManager::updateHostStatus(const vector<HostStatus>& value)
{
    lock_type lock(_mutex);
    for(auto & iter : value)
    {
        _host_status[iter.getUUID()] = iter;
        _host_counter[iter.getUUID()] = 0;
    }
}

void StatusManager::updateComputePoolStatus(const vector<ComputePoolStatus>& value)
{
    lock_type lock(_mutex);
    for(auto & iter : value)
    {
        _compute_pool_status[iter.getUUID()] = iter;
        _compute_pool_counter[iter.getUUID()] = 0;
    }
}

void StatusManager::updateServerRoomStatus(const vector<ServerRoomStatus>& value)
{
    lock_type lock(_mutex);
    for(auto & iter : value)
    {
        _server_room_status[iter.getUUID()] = iter;
        _server_room_counter[iter.getUUID()] = 0;
    }
}

void StatusManager::updateServerRackStatus(const vector<ServerRackStatus>& value)
{
    lock_type lock(_mutex);
    for(auto & iter : value)
    {
        _server_rack_status[iter.getUUID()] = iter;
        _server_rack_counter[iter.getUUID()] = 0;
    }
}

bool StatusManager::containsServerStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    return ((_server_status.count(uuid) == 1) ? true:false);
}

bool StatusManager::containsHostStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    return ((_host_status.count(uuid) == 1) ? true:false);
}

bool StatusManager::containsComputePoolStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    return ((_compute_pool_status.count(uuid) == 1) ? true:false);

}

bool StatusManager::containsServerRoomStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    return ((_server_room_status.count(uuid) == 1) ? true:false);

}

bool StatusManager::containsServerRackStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    return ((_server_rack_status.count(uuid) == 1) ? true:false);

}

bool StatusManager::containsSystemStatus()
{
    lock_type lock(_mutex);
    return _status.isVaild();
}
bool StatusManager::getServerStatus(const UUID_TYPE& uuid, ServerStatus& value)const
{
    lock_type lock(_mutex);

    auto status_iter = _server_status.find(uuid);
    if(status_iter != _server_status.end())
    {
        value = status_iter->second;
        return true;
    }

     return false;
}

bool StatusManager::getHostStatus(const UUID_TYPE& uuid, HostStatus& value)const
{
    lock_type lock(_mutex);

    auto status_iter = _host_status.find(uuid);
    if(status_iter != _host_status.end())
    {
        value = status_iter->second;
        return true;
    }

     return false;
}

bool StatusManager::getComputePoolStatus(const UUID_TYPE& uuid, ComputePoolStatus& value)const
{
    lock_type lock(_mutex);

    auto status_iter = _compute_pool_status.find(uuid);
    if(status_iter != _compute_pool_status.end())
    {
        value = status_iter->second;
    }

    return false;

}

bool StatusManager::getServerRoomStatus(const UUID_TYPE& uuid, ServerRoomStatus& value)const
{
    lock_type lock(_mutex);

    auto status_iter = _server_room_status.find(uuid);
    if(status_iter != _server_room_status.end())
    {
        value = status_iter->second;
    }

    return false;
}

bool StatusManager::getServerRackStatus(const UUID_TYPE& uuid, ServerRackStatus& value)const
{
    lock_type lock(_mutex);

    auto status_iter = _server_rack_status.find(uuid);
    if(status_iter != _server_rack_status.end())
    {
        value = status_iter->second;
    }

    return false;
}

bool StatusManager::getSystemStatus(SystemStatusMessage& value)const
{
    lock_type lock(_mutex);
    value = _status;
}

bool StatusManager::removeServerStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);

    auto status_iter = _server_status.find(uuid);
    if(status_iter != _server_status.end())
    {
        _server_status.erase(status_iter);
        return true;
    }

     return false;
}

bool StatusManager::removeHostStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);

    auto status_iter = _host_status.find(uuid);
    if(status_iter != _host_status.end())
    {
        _host_status.erase(status_iter);
        return true;
    }

    return false;

}

bool StatusManager::addHostStatus(const HostStatus& value)
{
    lock_type lock(_mutex);

    auto status_iter = _host_status.find(value.getUUID());
    if(status_iter != _host_status.end())
    {
        status_iter->second = value;
        return true;
    }
    return false;
}

bool StatusManager::changeHostStatus(const UUID_TYPE& uuid, const UnitStatusEnum& _status)
{
    lock_type lock(_mutex);

    auto status_iter = _host_status.find(uuid);
    if(status_iter != _host_status.end())
    {
        BaseCounter tmp(status_iter->second.getBaseCounter());
        tmp.setStatus(_status);
        status_iter->second.setBaseCounter(tmp);
        return true;
      }
    return false;
}

void StatusManager::getAllComputePoolStatus(vector<ComputePoolStatus>& list) const
{
    lock_type lock(_mutex);

    for(auto& item:_compute_pool_status)
    {
        list.emplace_back(item.second);
    }
}

void StatusManager::getAllServerRoomStatus(vector<ServerRoomStatus>& list) const
{
    lock_type lock(_mutex);

    for(auto& item:_server_room_status)
    {
        list.emplace_back(item.second);
    }
}

void StatusManager::getAllServerRackStatus(vector<ServerRackStatus>& list) const
{
    lock_type lock(_mutex);

    for(auto& item:_server_rack_status)
    {
        list.emplace_back(item.second);
    }
}

void StatusManager::getAllServerStatus(vector<ServerStatus>& list)const
{
    lock_type lock(_mutex);

    for(auto& item:_server_status)
    {
        list.emplace_back(item.second);
    }
}

void StatusManager::getAllHostStatus(vector<HostStatus>& list)const
{
    lock_type lock(_mutex);

    for(auto& item:_host_status)
    {
        list.emplace_back(item.second);
    }
}

bool StatusManager::removeComputePoolStatus(const UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    auto counter = _compute_pool_counter.find(uuid);
    if(counter!=_compute_pool_counter.end())
        _compute_pool_counter.erase(counter);

    auto status = _compute_pool_status.find(uuid);
    if(status!=_compute_pool_status.end())
    {
        _compute_pool_status.erase(status);
        return true;
    }

    return false;
}

void StatusManager::updateSystemStatus(const SystemStatusMessage& status)
{
    lock_type lock(_mutex);
    _status = status;
}

void StatusManager::statisticHostStatus(StatusCounter &counter)const
{
    lock_type lock(_mutex);
    for(auto& item : _host_status)
    {
        switch(item.second.getBaseCounter().getStatus())
        {
            case UnitStatusEnum::status_stop:
                counter.IncreaseStop();
            break;
            case UnitStatusEnum::status_warning:
                counter.IncreaseWarn();
            break;
            case UnitStatusEnum::status_error:
                counter.IncreaseError();
            break;
            case UnitStatusEnum::status_running:
                counter.IncreaseRun();
            break;
            default:
            break;
        }

    }
}



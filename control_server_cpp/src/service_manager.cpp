#include "service_manager.h"


using namespace zhicloud;
using namespace control_server;
using namespace util;

ServiceManager::ServiceManager(const string& logger_name)
{
   _logger = getLogger(logger_name);
}

ServiceManager::~ServiceManager()
{
    //dtor
}

void ServiceManager::addService(const ServiceStatus& service)
{
    if(_server_groups.count(service.getType()) == 0){

        map<string,set<string>> tmp;
        tmp["default"] = move(set<string>());
        _server_groups[service.getType()] = move(tmp);

    }
    _server_groups[service.getType()]["default"].emplace(service.getName());

    if(_service_in_server.count(service.getServer()) == 0){
        _service_in_server[service.getServer()] = move(set<string>());
    }

    _service_in_server[service.getServer()].emplace(service.getName());
    _service_map.emplace(service.getName(),service);//add new service
}

bool ServiceManager::activeService(const ServiceStatus& service)
{
    lock_type lock(_mutex);
    if(_service_map.count(service.getName()) == 0)
    {
        addService(service);
    }

    auto item = _service_map.find(service.getName());
    if( item == _service_map.end()){
        return false;
    }

    item->second.setIp(service.getIp());
    item->second.setPort(service.getPort());
    item->second.setVersion(service.getVersion());
    item->second.setServer(service.getServer());
    item->second.setStatus(UnitStatusEnum::status_running);


    return true;
}

bool ServiceManager::deactiveService(const ServiceStatus& service)
{
    lock_type lock(_mutex);
    auto item = _service_map.find(service.getName());
    if( item == _service_map.end()){
        return false;
    }

    auto iter = _whispers.find(service.getName());
    if(iter != _whispers.end())
        _whispers.erase(iter);

    item->second.setStatus(UnitStatusEnum::status_stop);
    return true;
}

bool ServiceManager::containsService(const string& name)
{
    lock_type lock(_mutex);
    return (_service_map.count(name) == 1 ? true : false);
}

bool ServiceManager::getService(const string& name,ServiceStatus& service)const
{
    lock_type lock(_mutex);
    auto item = _service_map.find(service.getName());
    if( item != _service_map.end()){
        service = item->second;
        return true;
    }
    return false;
}

void ServiceManager::deleteServiceFromServer(const UUID_TYPE& server_id,const string& service_name)
{
    auto service_list = _service_in_server.find(server_id);
    if(service_list != _service_in_server.end()){

        auto del_service = service_list->second.find(service_name);
        if(del_service != service_list->second.end())
            service_list->second.erase(del_service);

        if(service_list->second.size() == 0)
            _service_in_server.erase(service_list);

    }


}

void ServiceManager::loadService(const uint32_t& service_type, const vector<ServiceStatus>& service_list)
{
    lock_type lock(_mutex);
    map<string,ServiceStatus> new_service_map;
    for(const auto& service : service_list)
        new_service_map.emplace(service.getName(),service);

    //copy disk type
    for(auto& service : new_service_map)
    {
        auto old_service =_service_map.find(service.second.getName());
        if(old_service !=_service_map.end())
        {
            service.second.setDiskType(old_service->second.getDiskType());

        }
    }

    if(_server_groups.count(service_type))
    {
        //begin clear
        for(const auto &group : _server_groups[service_type])//map<group,set<service>>
        {
            for(const auto & service_name : group.second) //set<service>
            {
                auto old_service = _service_map.find(service_name);
                if(old_service != _service_map.end())
                {
                    deleteServiceFromServer(old_service->second.getServer(),service_name);
                    _service_map.erase(old_service);
                }

            }
        }

         auto default_group = _server_groups[service_type].find("default");
         if(default_group  != _server_groups[service_type].end())
            default_group->second.clear();

    }

    for(auto& service : new_service_map)
    {
        auto old_service =_service_map.find(service.first);
        if( old_service !=_service_map.end())
            _service_map.erase(old_service);

        addService(service.second);
    }

}

void ServiceManager::queryService(const uint32_t& service_type,const string& group_name,vector<ServiceStatus>& status_list)const
{
    lock_type lock(_mutex);
    //map<service_type,map<group_name,set<service_name>>> _server_groups;

    auto group =_server_groups.find(service_type);
    if( group == _server_groups.end())
        return;

    auto service_list = group->second.find(group_name);
    if( service_list == group->second.end())
        return;


    for(const auto& name : service_list->second)
    {
        const auto status = _service_map.find(name);
        if(status != _service_map.end()){
            status_list.emplace_back(status->second);
        }

    }
}

bool ServiceManager::updateService(const string& service_name,const ComputeStorageTypeEnum& type)
{
    lock_type lock(_mutex);
    auto item = _service_map.find(service_name);
    if( item != _service_map.end()){
        item->second.setDiskType(type);
        return true;
    }
    return false;
}


bool ServiceManager::queryServicesInServer(const UUID_TYPE& server,vector<string>& service_list)const
{
    lock_type lock(_mutex);
    auto item = _service_in_server.find(server);
    if( item != _service_in_server.end()){

        for(const auto & name :item->second)
            service_list.emplace_back(name);

        return true;
    }
    return false;
}

void ServiceManager::getAllServiceType(vector<uint32_t>& type_list)const
{
    lock_type lock(_mutex);
    for(const auto& item : _server_groups)
    {
        type_list.emplace_back(item.first);
    }
}

bool ServiceManager::queryServiceGroup(const uint32_t& service_type,vector<string>& group_list)const
{
    lock_type lock(_mutex);
    auto item = _server_groups.find(service_type);
    if( item != _server_groups.end()){

        for(const auto& group : item->second)
            group_list.emplace_back(group.first);

        return true;
    }
    return false;
}

 bool ServiceManager::updateWhisper(const string& service_name,const vector<WhisperService>& whisper_list)
 {
    lock_type lock(_mutex);
    auto item = _service_map.find(service_name);
    if( item != _service_map.end()){

        auto whisper_item =_whispers.find(service_name);
        if(whisper_item == _whispers.end())
        {
            _whispers[service_name] = move(vector<WhisperService>());
        }else{
            whisper_item->second.clear();
        }

        for(const auto& whisper : whisper_list){
            WhisperService tmp(whisper);
            tmp.setName(service_name);
            tmp.setType(item->second.getType());
            _whispers[service_name].emplace_back(tmp);
        }


        return true;
    }
    return false;
 }
bool ServiceManager::containsWhisper(const string& service_name)
{
    lock_type lock(_mutex);
    return (_whispers.count(service_name) == 1 ? true: false);
}

bool ServiceManager::getWhisper(const string& service_name,vector<WhisperService>& whisper_list)const
{
    lock_type lock(_mutex);
    auto item = _whispers.find(service_name);
    if( item != _whispers.end()){
        for(const auto &whisper : item->second)
        {
            whisper_list.emplace_back(whisper);
        }
        return true;
    }
    return false;
}

void ServiceManager::getAllWhisper(vector<WhisperService>& whisper_list)const
{
    lock_type lock(_mutex);
    for(const auto &item : _whispers)
    {
         for(const auto &whisper : item.second)
            whisper_list.emplace_back(whisper);
    }
}

void ServiceManager::statisticStatus(StatusCounter &counter)const
{
    lock_type lock(_mutex);
    for(const auto &item : _service_map)
    {
        switch(item.second.getStatus())
        {
            case UnitStatusEnum::status_stop:
            counter.IncreaseStop();
            break;
            case UnitStatusEnum::status_running:
            counter.IncreaseRun();
            break;
            case UnitStatusEnum::status_warning:
            counter.IncreaseWarn();
            break;
            case UnitStatusEnum::status_error:
            counter.IncreaseError();
            break;
            default:
            break;
        }
    }
}

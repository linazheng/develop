#include "expire_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;


const uint32_t ExpireManager::_tresource_type_host(0);
const uint32_t ExpireManager::_expire_type_found(0);
const uint32_t ExpireManager::_expire_type_lost(1);

ExpireManager::ExpireManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

ExpireManager::~ExpireManager()
{
    //dtor
}

bool ExpireManager::start(const string& resource_name)
{
    lock_type lock(_mutex);

    string found_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_found).str();
    _expire[found_name] = move(map<UUID_TYPE,uint32_t>());

    string lost_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_lost).str();
    _expire[found_name] = move(map<UUID_TYPE,uint32_t>());

    return true;
}

bool ExpireManager::updateFound(const string& resource_name, const set<UUID_TYPE>& id_list)
{
    string expire_key = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_found).str();
   return update(expire_key,id_list);
}

bool ExpireManager::updateLost(const string& resource_name, const set<UUID_TYPE>& id_list)
{
    string expire_key = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_lost).str();
    return update(expire_key,id_list);
}

bool ExpireManager::update(const string& target_name,const set<UUID_TYPE>& id_list)
{
    lock_type lock(_mutex);
    auto target_iter = _expire.find(target_name);
    if(target_iter != _expire.end() )
    {
        map<UUID_TYPE,uint32_t>& target = target_iter->second;
        for(auto& id : id_list)
        {
            auto found_iter = target.find(id);
            if(found_iter == target.end())
                target.emplace(id,1);//new
            else
                found_iter->second +=1;
        }

        auto del_iter = target.begin();
        for(;del_iter!= target.end();)
        {
            if(id_list.count(del_iter->first) == 0)
            {
                target.erase(del_iter++);
            }else{
                del_iter++;
            }
        }
    }

    return false;
}

bool ExpireManager::isFound(const string& resource_name,const UUID_TYPE& uuid,const uint32_t & max_expire)
{
    string found_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_found).str();
    return check(found_name,uuid,max_expire);

}
bool  ExpireManager::isLost(const string& resource_name,const UUID_TYPE& uuid,const uint32_t & max_expire)
{
    string lost_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_lost).str();
    return check(lost_name,uuid,max_expire);
}

bool ExpireManager::check(const string& target_name,const UUID_TYPE& uuid,const uint32_t & max_expire)
{
    lock_type lock(_mutex);

    auto target_iter = _expire.find(target_name);
    if(target_iter != _expire.end() )
    {
        auto iter = target_iter->second.find(uuid);
        if(iter ==  target_iter->second.end())
            return false;

        iter->second +=1;
        if(iter->second < max_expire )
            return false;

        target_iter->second.erase(iter);
             return true;
    }
    return false;
}

bool  ExpireManager::finish(const string& resource_name)
{
    lock_type lock(_mutex);
    string found_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_found).str();
    auto found_iter = _expire.find(found_name);
    if(found_iter != _expire.end() )
        _expire.erase(found_iter);

    string lost_name = (boost::format("%d_%s_%d") %_tresource_type_host %resource_name %_expire_type_lost).str();
    auto lost_iter = _expire.find(lost_name);
    if(lost_iter != _expire.end() )
        _expire.erase(lost_iter);

    return true;
}

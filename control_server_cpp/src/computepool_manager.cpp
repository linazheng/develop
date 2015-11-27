#include "computepool_manager.h"

#include <util/generator.h>


using namespace zhicloud;
using namespace control_server;
using namespace util;

ComputePoolManager::ComputePoolManager(const string& resource_path,const string& logger_name)
{
    _logger = getLogger(logger_name);

    stringstream ss;
    ss << resource_path << "compute/";
    _pool_path = ss.str();///var/zhicloud/config/control_server/resource/compute/

    if(! boost::filesystem::exists(_pool_path))
        boost::filesystem::create_directory(_pool_path);

	ss << "compute_pool.info";
	_pool_config = ss.str();
}

ComputePoolManager::~ComputePoolManager()
{

}

bool ComputePoolManager::load()
{
    lock_type lock(_mutex);
    try{
        if(!loadAllPool())
        {
            //add default pool
            ComputePool pool;
            pool.setName("default");
            if(!createPool(pool))
            {
                _logger->info("<ComputePoolManager> create default pool failed");
                return false;
            }
            _default_pool = pool.getUUID();
            _logger->info("<ComputePoolManager> create default pool ok");
            }else{
            const auto iter = _compute_pool.begin();
            if(iter != _compute_pool.end())
            {
             _default_pool = iter->first;
            }
        }
    }catch(std::exception &ex) {
        _logger->error(boost::format("<ConfigManager> load exception: %s")%ex.what());
        return false;
    }

	return true;
}

 bool ComputePoolManager::loadAllPool()
 {
 	lock_type lock(_mutex);

	if(!boost::filesystem::exists(_pool_config)){
		_logger->info(boost::format("<ComputePoolManager> config name '%s' not found") %_pool_config);
		return false;
	}


    boost::property_tree::ptree parser;
    boost::property_tree::ini_parser::read_ini(_pool_config, parser);

	uint32_t data_count = parser.get<uint32_t>("DEFAULT.data_count");

	if( 0 == data_count )
		return false;

	for(uint32_t index =0;index< data_count;index++){
		string pool_uuid = parser.get<string>((boost::format("DEFAULT.uuid_%d")%index).str());

		//read /var/zhicloud/config/control_server/resource/compute/uuid/pool.info

                stringstream ss;
                ss << _pool_path << pool_uuid<<"/pool.info";
                string pool_name = ss.str();

		if(!boost::filesystem::exists(pool_name)){
                     _logger->error(boost::format("<ComputePoolManager>  pool.info not exist '%s'") %pool_name.c_str());
                    continue;
		}


		boost::property_tree::ptree pool_parser;
		boost::property_tree::ini_parser::read_ini(pool_name, pool_parser);

		ComputePool pool;
		pool.setName(pool_parser.get<string>("DEFAULT.name"));
		pool.setUUID(pool_parser.get<string>("DEFAULT.uuid"));
		pool.setStatus(OptionStatusEnum(pool_parser.get<uint32_t>("DEFAULT.status")));
		pool.setNetwork(pool_parser.get<string>("DEFAULT.network"));
		pool.setNetworkType(ComputeNetworkTypeEnum(pool_parser.get<uint32_t>("DEFAULT.network_type")));
		pool.setStorageType(ComputeStorageTypeEnum(pool_parser.get<uint32_t>("DEFAULT.disk_type")));
		pool.setDisk(pool_parser.get<string>("DEFAULT.disk_source"));

		if(pool_parser.get_child_optional("DEFAULT.high_available")){
			pool.setHighAvaliableMode(HighAvaliableModeEnum(pool_parser.get<uint32_t>("DEFAULT.high_available")));
		}

		if(pool_parser.get_child_optional("DEFAULT.auto_qos")){
			pool.setAutoQOSMode(AutoQOSModeEnum(pool_parser.get<uint32_t>("DEFAULT.auto_qos")));
		}

		if(pool_parser.get_child_optional("DEFAULT.path")){
			pool.setPath(pool_parser.get<string>("DEFAULT.path"));
		}

		if(pool_parser.get_child_optional("DEFAULT.crypt")){
			pool.setCrypt(pool_parser.get<string>("DEFAULT.crypt"));
		}

		if(pool_parser.get_child_optional("DEFAULT.thin_provisioning")){
			pool.setThinProvisioningMode(ThinProvisioningModeEnum(pool_parser.get<uint32_t>("DEFAULT.thin_provisioning")));
		}

		if(pool_parser.get_child_optional("DEFAULT.backing_image")){
			pool.setBackingImageMode(BackingImageModeEnum(pool_parser.get<uint32_t>("DEFAULT.backing_image")));
		}

		//begin resource
		uint32_t resource_count = pool_parser.get<uint32_t>("DEFAULT.resource_count");
		if(resource_count > 0){

			for(uint32_t resource_index =0;resource_index< resource_count;resource_index++)
			{
				string resource_name = pool_parser.get<string>((boost::format("DEFAULT.resource_%d")%resource_index).str());
				stringstream tmp;
                                   tmp << _pool_path <<pool_uuid<<"/resource_"<< resource_name<<".info";
				resource_name = tmp.str();

				if(!boost::filesystem::exists(resource_name)){
                                     _logger->error(boost::format("<ComputePoolManager>  resource.info not exist '%s'") %resource_name.c_str());
                                    continue;
				}

                                   _logger->info(boost::format("<ComputePoolManager> begin read '%s'") %resource_name.c_str());
				//read /var/zhicloud/config/control_server/resource/compute/uuid/resource.info
				boost::property_tree::ptree resource_parser;
				boost::property_tree::ini_parser::read_ini(resource_name, resource_parser);

				ComputeResource resource;
				resource.setName(resource_parser.get<string>("DEFAULT.name"));
				resource.setServerUUID(resource_parser.get<string>("DEFAULT.server"));
				resource.setStatus(OptionStatusEnum(resource_parser.get<uint32_t>("DEFAULT.status")));

				uint32_t host_count = resource_parser.get<uint32_t>("DEFAULT.host_count");
				for(uint32_t host_index = 0;host_index < host_count;host_index++){
					UUID_TYPE host_id = resource_parser.get<string>((boost::format("DEFAULT.host_%d")%host_index).str());
					resource.setHost(host_id);
				}
				pool.setResource(resource.getName(),resource);
				_logger->info(boost::format("<ComputePoolManager> pool '%s' add resource '%s'") %pool.getUUID().c_str() %resource.getName().c_str());

			}
		}

		_compute_pool.emplace(pool.getUUID(),pool);
		_logger->info(boost::format("<ComputePoolManager> add pool '%s'") %pool.getUUID().c_str());

	}

	return true;
 }


 bool ComputePoolManager::savePoolList()
 {
 	lock_type lock(_mutex);
 	if(_compute_pool.size() > 0){
        boost::property_tree::ptree parser;
        parser.put<uint32_t>("DEFAULT.data_count", uint32_t(_compute_pool.size()));

        uint32_t index = 0;
        boost::filesystem::directory_iterator end_iter;
        for (boost::filesystem::directory_iterator iter(_pool_path); iter!=end_iter; ++iter)
        {
            if (boost::filesystem::is_directory(iter->status()))
            {
                string name = iter->path().filename().string();
                auto iter = _compute_pool.find(name);
                if(iter !=  _compute_pool.end())
                {
                    string pool_name = (boost::format("DEFAULT.uuid_%d")%index).str();
                    index +=1;
                    parser.put<string>(pool_name,name);
                }else{
                    _logger->info(boost::format("<ComputePoolManager> invild pool '%s'") %name.c_str());
                }
            }
        }

        try {
            boost::property_tree::ini_parser::write_ini(_pool_config, parser);
            _logger->info(boost::format("<ComputePoolManager> savePoolList pool list to '%s'") %_pool_config);
         }catch(std::exception &ex) {
            _logger->error(boost::format("<ConfigManager> savePoolList exception: %s")%ex.what());
         }
    }
	return true;
 }

bool ComputePoolManager::savePoolInfo(const UUID_TYPE& pool_id)
{
    lock_type lock(_mutex);
    auto iter =_compute_pool.find(pool_id);
    if(iter != _compute_pool.end()){
        const ComputePool& pool = iter->second;
        boost::property_tree::ptree parser;

        parser.put<string>("DEFAULT.name", pool.getName());
        parser.put<string>("DEFAULT.uuid", pool.getUUID());
        parser.put<uint32_t>("DEFAULT.status", uint32_t(pool.getStatus()));
        parser.put<string>("DEFAULT.network", pool.getNetWork());
        parser.put<uint32_t>("DEFAULT.network_type", uint32_t(pool.getNetWorkType()));
        parser.put<string>("DEFAULT.disk_source", pool.getDisk());
        parser.put<uint32_t>("DEFAULT.disk_type", uint32_t(pool.getStorageType()));
        parser.put<uint32_t>("DEFAULT.high_available", uint32_t(pool.getHighAvaliableMode()));
        parser.put<uint32_t>("DEFAULT.auto_qos", uint32_t(pool.getAutoQOSMode()));
        parser.put<uint32_t>("DEFAULT.thin_provisioning", uint32_t(pool.getThinProvisioningMode()));
        parser.put<uint32_t>("DEFAULT.backing_image", uint32_t(pool.getBackingImageMode()));
        parser.put<string>("DEFAULT.path", pool.getPath());
        parser.put<string>("DEFAULT.crypt", pool.getCrypt());

        const map<string,ComputeResource>& resource_lits = pool.getResourceList();
        uint32_t resource_count = resource_lits.size();
        parser.put<uint32_t>("DEFAULT.resource_count",resource_count);

        uint32_t index = 0;
        for(const auto& item :resource_lits){
            string name = (boost::format("DEFAULT.resource_%d")%index).str();
            index +=1;
            parser.put<string>(name, item.second.getName());
        }


        try{
            stringstream ss;
            ss << _pool_path << pool_id;

            if(!boost::filesystem::exists(ss.str()))
                boost::filesystem::create_directory(_pool_path);

            ss <<"/pool.info";

            boost::property_tree::ini_parser::write_ini(ss.str(), parser);
            _logger->info(boost::format("<ComputePoolManager> savePoolInfo pool id '%s' to '%s'") %pool_id.c_str() %_pool_config.c_str());
            return true;
        }catch(std::exception &ex) {
            _logger->error(boost::format("<ConfigManager> savePoolInfo exception: %s")%ex.what());
         }


    }
    _logger->error(boost::format("<ComputePoolManager> savePoolInfo fail,invaild pool id %s") %pool_id.c_str());
	return false;

}

bool ComputePoolManager::savePoolResource(const UUID_TYPE& pool_id,const UUID_TYPE& resource_name)
{
    lock_type lock(_mutex);
    ComputeResource resource;

    if(getResource(pool_id,resource_name,resource))
    {
        boost::property_tree::ptree parser;
        parser.put<string>("DEFAULT.name", resource.getName());
        parser.put<string>("DEFAULT.server", resource.getServerUUID());
        parser.put<uint32_t>("DEFAULT.status", uint32_t(resource.getStatus()));

        const set<UUID_TYPE>& host_list = resource.getHostList();
        uint32_t host_count = host_list.size();
        parser.put<uint32_t>("DEFAULT.host_count", host_count);
        uint32_t index = 0;
        for(const auto& host:host_list )
        {
            string name = (boost::format("DEFAULT.host_%d")%index).str();
            index +=1;
            parser.put<string>(name, host);

        }

        try{
            stringstream ss;
            ss << _pool_path << pool_id << "/";

            if(! boost::filesystem::exists(ss.str()))
                boost::filesystem::create_directory(ss.str());

            string path = (boost::format("resource_%s.info")%resource_name).str();
            ss << path;
            path = ss.str();


            boost::property_tree::ini_parser::write_ini(path, parser);
            _logger->info(boost::format("<ComputePoolManager> savePoolResource pool id '%s' to '%s'") %pool_id.c_str() %path.c_str());
            return true;
        }catch(std::exception &ex) {
            _logger->error(boost::format("<ConfigManager> savePoolResource exception: %s")%ex.what());
         }

    }
    _logger->error(boost::format("<ComputePoolManager> savePoolResource fail,invaild pool id '%s'") %pool_id.c_str());
    return false;
}

void ComputePoolManager::deleteResourceFile(const UUID_TYPE& pool_id,const UUID_TYPE& resource_name)
{
    lock_type lock(_mutex);
    stringstream ss;
    string path = (boost::format("resource_%s.info")%resource_name).str();
    ss << _pool_path << pool_id <<"/"<<path;
    path = ss.str();

    if(boost::filesystem::exists(path))
        boost::filesystem::remove(path);

}

void ComputePoolManager::deletePoolPath(const UUID_TYPE& pool_id)
{
    lock_type lock(_mutex);
    stringstream ss;
    ss << _pool_path << pool_id;
    string path = ss.str();

    if(boost::filesystem::exists(path))
        boost::filesystem::remove_all(path);
}

void ComputePoolManager::getDefaultPoolID(string &pool_id) const
{
	pool_id = _default_pool;
}

 bool ComputePoolManager::getDefaultPool(ComputePool &pool) const
 {
     return getPool(_default_pool,pool);
 }

 void ComputePoolManager::queryAllPool(map<UUID_TYPE,ComputePool> &compute_pool) const
 {
    lock_type lock(_mutex);
    for(auto & item :_compute_pool)
    {
        compute_pool.emplace(item);
    }
 }

bool ComputePoolManager::createPool(ComputePool &pool)
{
    lock_type lock(_mutex);

    for(const auto& item : _compute_pool)
    {
        if(item.second.getName() == pool.getName())
        {
            _logger->error(boost::format("<ComputePoolManager> createPool faild, already exists name '%s'") %pool.getName().c_str());
            return false;
        }
    }

    Generator gen;
    pool.setUUID(gen.uuid_hex());
    if(_compute_pool.count(pool.getUUID()) == 0)
    {
        pool.setStatus(OptionStatusEnum::enabled);

        _compute_pool.emplace(pool.getUUID(),pool);
         _logger->info(boost::format("<ComputePoolManager> createPool ok '%s'") %pool.getUUID().c_str());
        savePoolList();
        savePoolInfo(pool.getUUID());

        return true;
    }else{
        _logger->error(boost::format("<ComputePoolManager> createPool faild already exists '%s'") %pool.getUUID().c_str());
    }
	return false;
}

bool ComputePoolManager::modifyPool(const ComputePool &pool)
{
    lock_type lock(_mutex);
    auto iter = _compute_pool.find(pool.getUUID());
    if(iter != _compute_pool.end())
    {
        ComputePool &target = iter->second;
        if(target.getUUID() != pool.getUUID() && target.getName() == pool.getName() )
        {
             _logger->error(boost::format("<ComputePoolManager> modifyPool fail pool id '%s',duplicate pool name '%s'") %pool.getUUID().c_str() %pool.getName().c_str());
             return false;
        }


        target.setName(pool.getName());
        target.setStatus(pool.getStatus());
        target.setNetwork(pool.getNetWork());
        target.setNetworkType(pool.getNetWorkType());
        target.setDisk(pool.getDisk());
        target.setStorageType(pool.getStorageType());
        target.setHighAvaliableMode(pool.getHighAvaliableMode());
        target.setAutoQOSMode(pool.getAutoQOSMode());
        target.setThinProvisioningMode(pool.getThinProvisioningMode());
        target.setBackingImageMode(pool.getBackingImageMode());
        target.setPath(pool.getPath());
        target.setCrypt(pool.getCrypt());

        savePoolInfo(pool.getUUID());
        _logger->info(boost::format("<ComputePoolManager> modifyPool ok pool id '%s',pool name '%s'") %pool.getUUID().c_str() %pool.getName().c_str());
        return false;
    }


    _logger->error(boost::format("<ComputePoolManager> modifyPool fail,invaild pool id '%s'") %pool.getUUID().c_str());
	return false;
}

bool ComputePoolManager::deletePool(const UUID_TYPE& pool_id)
{
    lock_type lock(_mutex);
    auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        if(!iter->second.isEmpty()){
            _logger->error(boost::format("<ComputePoolManager> deletePool faild, pool id '%s' not empty") %pool_id.c_str());
            return false;
        }
        _compute_pool.erase(iter);
        deletePoolPath(pool_id);
        savePoolList();
        //TODO:if delete default pool ,the _default_pool need to been sync ?
        /*if(_default_pool == pool_id)
        {
            _default_pool = "";
            if(_compute_pool.begin() != _compute_pool.end())
            {
                _default_pool = _compute_pool.begin()->first;
            }
        }*/
        _logger->error(boost::format("<ComputePoolManager> deletePool faild,invaild pool id '%s'") %pool_id.c_str());
        return true;
    }
    _logger->info(boost::format("<ComputePoolManager> deletePool success,invaild pool id '%s'") %pool_id.c_str());
    return false;
}

bool ComputePoolManager::containsPool(const UUID_TYPE& pool_id) const
{
    lock_type lock(_mutex);
    return ((_compute_pool.count(pool_id) == 1) ? true:false);
}

bool ComputePoolManager::getPool(const UUID_TYPE& pool_id, ComputePool &pool) const
{
    lock_type lock(_mutex);

    const auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        pool = iter->second;
        return true;
    }
     _logger->info(boost::format("<ComputePoolManager> getPool faild,invaild pool id '%s'") %pool_id.c_str());
	return false;
}

bool ComputePoolManager::addResource(const UUID_TYPE& pool_id,vector<ComputeResource>& resource_list)
{
    lock_type lock(_mutex);

    auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        bool savepool  = false;
        ComputePool& pool = iter->second;
        for(auto &item : resource_list)
        {
            if(!pool.containResource(item.getName()))
            {
                item.setStatus(OptionStatusEnum::enabled);
                pool.setResource(item.getName(),item);
                savePoolResource(pool.getUUID(),item.getName());
                savepool = true;
                 _logger->info(boost::format("<ComputePoolManager> addResource success,add resource '%s' to '%s'") %item.getName().c_str() %pool_id.c_str());
            }

        }

        if(savepool)
            savePoolInfo(pool.getUUID());

        return true;
    }
    _logger->error(boost::format("<ComputePoolManager> addResource faild,invaild pool id '%s'") %pool_id.c_str());
	return false;
}

bool ComputePoolManager::removeResource(const UUID_TYPE& pool_id,const vector<string>& name_list)
{
    lock_type lock(_mutex);

    auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        bool savepool = false;
        for(const auto& name :name_list)
        {
            const map<string,ComputeResource> & resource_list = iter->second.getResourceList();
            auto resource = resource_list.find(name);
            if(resource != resource_list.end() && resource->second.getHostSize() > 0)
            {
                 _logger->error(boost::format("<ComputePoolManager> removeResource faild '%s', resource '%s' not empty") %pool_id.c_str() %name.c_str());
                continue;

            }else if(resource != resource_list.end())
            {
                deleteResourceFile(pool_id,name);
                savepool = true;
            }
        }

        if(savepool)
            savePoolInfo(pool_id);

        return true;
    }
     _logger->error(boost::format("<ComputePoolManager> removeResource faild,invaild pool id '%s'") %pool_id.c_str());
	return false;
}

void ComputePoolManager::queryResource(const UUID_TYPE& pool_id,vector<ComputeResource>& resource_list) const
{
    lock_type lock(_mutex);
    const auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        const map<string,ComputeResource> & computeresource = iter->second.getResourceList();
        for(const auto & item :computeresource){
            resource_list.emplace_back(item.second);
        }
    }
}

bool ComputePoolManager::searchResource(const string& name,UUID_TYPE& uuid)
{
    lock_type lock(_mutex);
    for(const auto& item :_compute_pool)
	{
        ComputeResource resource;
        if(getResource(item.second.getUUID(),name,resource))
        {
            uuid = resource.getServerUUID();
            return true;
        }

	}

    return false;
}

bool ComputePoolManager::containsResource(const UUID_TYPE& pool_id,const string& name)
{
	lock_type lock(_mutex);

    const auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        return iter->second.containResource(name);

    }
	return false;
}

bool ComputePoolManager::getResource(const UUID_TYPE& pool_id,const string& name,ComputeResource &resource) const
{
    lock_type lock(_mutex);
    const auto iter = _compute_pool.find(pool_id);
    if(iter != _compute_pool.end())
    {
        const map<string,ComputeResource> &ResourceList = iter->second.getResourceList();
        const auto resource_iter = ResourceList.find(name);
        if(resource_iter !=  ResourceList.end())
        {
            resource = resource_iter->second;
            return true;
        }else{
            return false;
        }

    }

	return false;
}

bool ComputePoolManager::containNetwork(const UUID_TYPE& network)
{
	if(0 == network.size())
		return false;

	lock_type lock(_mutex);
	for(const auto& item :_compute_pool)
	{
		if(item.second.getNetWork() == network)
			return true;
	}
	return false;
}


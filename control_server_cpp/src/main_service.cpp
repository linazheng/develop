#include "main_service.h"

#include <boost/filesystem.hpp>
#include <exception>
#include "task_session.hpp"

using namespace zhicloud;
using namespace zhicloud::control_server;

const string MainService::version("2.1#20151113-1");
const string MainService::config_root("/var/zhicloud/config/control_server/");
const uint32_t MainService::monitor_timer_session(1);
uint32_t MainService::monitor_timer_id(0);
const uint32_t MainService::monitor_interval(2);

const uint32_t MainService::status_timer_session(2);
uint32_t MainService::status_timer_id(0);
const uint32_t MainService::status_interval(5);

const uint32_t MainService::statistic_timer_session(3);
uint32_t MainService::statistic_timer_id(0);
const uint32_t MainService::statistic_interval(60);

const uint32_t MainService::synchronize_timer_session(4);
uint32_t MainService::synchronize_timer_id(0);
const uint32_t MainService::synchronize_interval(1);

const uint32_t MainService::storage_server_timer_session(5);
uint32_t MainService::storage_server_timer_id(0);
const uint32_t MainService::storage_server_interval(10);

const uint32_t MainService::_transaction_thread(5);
const uint32_t MainService::_max_statistic_timeout(5);

MainService::MainService(const string& service_name, const string& domain, const string& ip, const string& group_ip, const uint16_t& group_port, const string& server,
        const string& rack, const string& server_name):
    NodeService(ServiceType::control_server, service_name, domain, ip, (5600+(uint32_t)ServiceType::control_server), 200, group_ip, group_port, version, server, rack, server_name)
{
    stringstream ss;
    ss << config_root << "resource/";
    const string data_source = ss.str();

    if(! boost::filesystem::exists(data_source))
        boost::filesystem::create_directory(data_source);

    _computepool_manager =  boost::shared_ptr<ComputePoolManager>(new ComputePoolManager(data_source,service_name));
    _status_manager =  boost::shared_ptr<StatusManager>(new StatusManager(service_name));
    _config_manager =  boost::shared_ptr<ConfigManager>(new ConfigManager(service_name));
    _monitor_manager=  boost::shared_ptr<MonitorManager>(new MonitorManager(service_name));
    _service_manager =  boost::shared_ptr<ServiceManager>(new ServiceManager(service_name));
    _expire_manager =  boost::shared_ptr<ExpireManager>(new ExpireManager(service_name));

    this->initialize();

}

MainService::~MainService() {}

bool MainService::initialize()
{

    _statistic_timeout = 0;

    if(!_computepool_manager->load())
        return false;


     _clienttrans_manager =  boost::shared_ptr<ClientTransManager>(new ClientTransManager(this,
                                                                        *_computepool_manager,
                                                                        *_status_manager,
                                                                        *_config_manager,
                                                                        *_service_manager,
                                                                        *_expire_manager,
                                                                         _transaction_thread));

    console(boost::format("<ControlService>%s initilized") %fullname);

    logger->info(boost::format("<ControlService>%s initilized")
            %fullname);

    return true;
}

bool MainService::onStart()
{

    if(!NodeService::onStart())
        return false;

    monitor_timer_id = setLoopTimer(monitor_interval, monitor_timer_session);
    status_timer_id = setLoopTimer(status_interval, status_timer_session);
    synchronize_timer_id = setLoopTimer(synchronize_interval, synchronize_timer_session);
    storage_server_timer_id = setLoopTimer(storage_server_interval, storage_server_timer_session);

    _clienttrans_manager->start();

    logger->info("<ControlService>main service start success.");
    return true;
}

void MainService::onStop()
{

    clearTimer(monitor_timer_id);
    clearTimer(status_timer_id);
    clearTimer(statistic_timer_id);
    clearTimer(synchronize_timer_id);
    clearTimer(storage_server_timer_id);

    NodeService::onStop();
}

void MainService::onChannelConnected(const string& node_name, const ServiceType& node_type, const string& remote_ip, const uint16_t& remote_port)
{
    logger->info(boost::format("<ControlService>channel connected, node name '%s', type: %d")
            %node_name %(uint32_t)node_type);
    switch((ServiceType)node_type)
    {
        case ServiceType::node_client:
            return onClientConnected(node_name);
        break;
        case ServiceType::data_server:
            return onDataServerConnected(node_name);
        break;
        case ServiceType::storage_server:
            return onStorageConnected(node_name);
        break;
        case ServiceType::intelligent_router:
            return onIntelligentRouterConnected(node_name);
        break;
        case ServiceType::data_index:
            return onDataIndexConnected(node_name);
        break;
        default:
        break;
    }

}

void MainService::onChannelDisconnected(const string& node_name, const ServiceType& node_type)
{
    logger->info(boost::format("<ControlService>channel disconnected, node name '%s', type: %d")
            %node_name %(uint32_t)node_type);
    switch((ServiceType)node_type)
    {
        case ServiceType::node_client:
            return onClientDisconnected(node_name);
        break;
        case ServiceType::storage_server:
            return onStorageDisconnected(node_name);
        break;
        case ServiceType::intelligent_router:
            return onIntelligentRouterDisconnected(node_name);
        break;
        case ServiceType::statistic_server:
            return onStatisticServerDisconnected(node_name);
        break;
        default:
        break;
    }
}

void MainService::handleEventMessage(AppMessage& event, const string& sender)
{
     try{

         if(0 != event.session) {
            if(_clienttrans_manager->containsTransaction(event.session)) {
                _clienttrans_manager->processMessage(event.session, event);
                return;
            }
        }

        switch((EventEnum)event.id)
        {
            case EventEnum::timeout:
                 return handleTimeout(event, sender);
            break;
            case EventEnum::service_status_changed:
                return handleServiceStatusChanged(event, sender);
            break;
            case EventEnum::monitor_heart_beat:
                return handleMonitorHeartBeat(event, sender);
            break;
            case EventEnum::keep_alive:
                return handleKeepAlive(event, sender);
            break;
            default:
             logger->info(boost::format("<ControlService> ignore event %d from '%s'") %event.id %sender);
            break;
        }


    } catch(std::exception &ex) {
        logger->error(boost::format("<ControlService> handle event exception, request %d, sender '%s' , messasge:%s")%event.id%sender%ex.what());
    }

}

void MainService::handleRequestMessage(AppMessage& request,const string& sender)
{
    try{
        uint32_t session_id = 0;
        switch((RequestEnum)request.id)
        {
            case RequestEnum::start_monitor:
                return handleStartMonitorRequest(request, sender);
            break;
            case RequestEnum::stop_monitor:
                return handleStopMonitorRequest(request, sender);
            break;
            case RequestEnum::start_statistic:
                return handleStartStatisticRequest(request, sender);
            break;
            case RequestEnum::stop_statistic:
                return handleStopStatisticRequest(request, sender);
            break;
            case RequestEnum::query_compute_pool:
                _clienttrans_manager->startTransaction(TaskType::query_compute_pool, request, session_id);
            break;
            default:
             logger->info(boost::format("<ControlService> ignore request %d from '%s'") %request.id %request.sender);
            break;
        }


    } catch(std::exception &ex) {
        logger->error(boost::format("<ControlService> handle request exception, request %d, sender '%s' , messasge:%s")%request.id%sender%ex.what());
    }

}


void MainService::handleResponseMessage(AppMessage& response,const string& sender)
{
    try {
        if(0 != response.session) {
            if(_clienttrans_manager->containsTransaction(response.session)) {
                _clienttrans_manager->processMessage(response.session, response);
                return;
            }
        }
        logger->info(boost::format("<ControlService> ignore response id %d from '%s'")%response.id %sender);

    } catch(std::exception &ex) {
        logger->error(boost::format("<ControlService> handle response exception, response %d, sender '%s', messasge:%s")%response.id%sender%ex.what());
    }
}

void MainService::onTransportEstablished(const string& ip, const uint16_t& port)
{
}

void MainService::handleTimeout(AppMessage& event, const string& sender)
{
    if(event.session == monitor_timer_session)
        return handleMonitorTimeout();
    else if(event.session == status_timer_session)
        return onStatusCheckTimeout();
    else if(event.session == statistic_timer_session)
        return handleStatisticCheckTimeout();
    else if(event.session == synchronize_timer_session)
        return handleSynchronizeTimeout();
    else if(event.session == synchronize_timer_session)
        return handleStorageServerSyncTimeout();

}

void MainService::handleServiceStatusChanged(AppMessage& event, const string& sender)
{

}

void MainService::handleMonitorHeartBeat(AppMessage& event, const string& sender)
{
    uint32_t task_id = 0;
    event.getUInt(ParamEnum::task,task_id);

    if(task_id > 0)
        _monitor_manager->processHeartBeat(task_id);
}

void MainService::handleKeepAlive(AppMessage& event, const string& sender)
{
    if(event.session == statistic_timer_session)
    {
        return handleStatisticKeepAlive();
    }

}

void MainService::handleNotifyTimeout()
{
}

void MainService::onClientConnected(const string& node_name)
{
    uint32_t session_id = 0;
    if(_sync_session.count(node_name))
    {
        AppMessage request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::initial_node, request, session_id);
        _sync_session.emplace(node_name,session_id);
        logger->info(boost::format("<control_service> start sync data with node '%s', session [%08X]") %node_name %session_id);
    }

    if(_observe_session.count(node_name))
    {
        AppMessage request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        request.setString(ParamEnum::target, node_name);
        request.setString(ParamEnum::name, server_name);
        _clienttrans_manager->startTransaction(TaskType::start_observe, request, session_id);
        _observe_session.emplace(node_name,session_id);
        logger->info(boost::format("<control_service> start observe with node '%s', session [%08X]") %node_name %session_id);
    }

    AppMessage request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
    request.setString(ParamEnum::target, node_name);
    _clienttrans_manager->startTransaction(TaskType::synch_service_status, request, session_id);
    logger->info(boost::format("<control_service> start sync service status with node '%s', session [%08X]") %node_name %session_id);
}

void MainService::onDataServerConnected(const string& node_name)
{
    uint32_t session_id = 0;
    //load service
    AppMessage service_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
    service_request.setString(ParamEnum::target, node_name);
    _clienttrans_manager->startTransaction(TaskType::load_service, service_request, session_id);

     //load config
    AppMessage config_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
    config_request.setString(ParamEnum::target, node_name);
    _clienttrans_manager->startTransaction(TaskType::load_config, config_request, session_id);
}

void MainService::onStorageConnected(const string& node_name)
{
    lock_type lock(_storage_server_mutex);
    if(_storage_server.count(node_name) == 0)
    {
        _storage_server.emplace(node_name);
        uint32_t session_id = 0;
        //initial storage : query iso image and disk image
        AppMessage init_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        init_request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::initial_storage, init_request, session_id);

         //storage server sync : query whisper
        AppMessage sync_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        sync_request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::storage_server_sync, sync_request, session_id);

        //synch storage_server status
        AppMessage syncservice_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        syncservice_request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::synch_service_status, syncservice_request, session_id);

    }
}

void MainService::onIntelligentRouterConnected(const string& node_name)
{
    lock_type lock(_intelligent_router_mutex);
    if(_intelligent_router.count(node_name) == 0)
    {
        _intelligent_router.emplace(node_name);
    }
}

void MainService::onDataIndexConnected(const string& node_name)
{
    lock_type lock(_data_indexes_mutex);
    if(_data_indexes.count(node_name) == 0)
    {
        _data_indexes.emplace(node_name);
        uint32_t session_id = 0;

        // initialize storage pool
        AppMessage storge_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        storge_request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::initial_storage_pool, storge_request, session_id);

         // initialize snapshot pool
        AppMessage snapshot_request(AppMessage::message_type::REQUEST, RequestEnum::invalid);
        snapshot_request.setString(ParamEnum::target, node_name);
        _clienttrans_manager->startTransaction(TaskType::initial_snapshot_pool, snapshot_request, session_id);


    }
}

void MainService::onClientDisconnected(const string& node_name)
{
    auto sync = _sync_session.find(node_name);
    if(sync !=  _sync_session.end())
    {
        _clienttrans_manager->terminateTransaction(sync->second);
        _sync_session.erase(sync);
    }

    auto observe = _observe_session.find(node_name);
    if(observe !=  _observe_session.end())
    {
        _clienttrans_manager->terminateTransaction(observe->second);
        _observe_session.erase(observe);
    }
}


void MainService::onStorageDisconnected(const string& node_name)
{
    lock_type lock(_storage_server_mutex);
    auto storge = _storage_server.find(node_name);
    if(storge != _storage_server.end() )
        _storage_server.erase(storge);
}

void MainService::onIntelligentRouterDisconnected(const string& node_name)
{
    lock_type lock(_intelligent_router_mutex);
    auto router = _intelligent_router.find(node_name);
    if(router != _intelligent_router.end() )
        _intelligent_router.erase(router);

}

void MainService::onStatisticServerDisconnected(const string& node_name)
{
    if(_statistic_server != node_name)
        return;
    if(statistic_timer_id != 0)
    {
        clearTimer(statistic_timer_id);
        statistic_timer_id = 0;
        _statistic_server ="";
        logger->info(boost::format("statistic server disconnected, stop report for server %s") %node_name);
    }
}

void MainService::handleStartMonitorRequest(AppMessage& event, const string& sender)
{
    MonitorTask task;
    task.setReceivedNode(sender);
    task.setReceivedSession(event.session);
    vector<string> target_list;
    event.getStringArray(ParamEnum::target,target_list);
    task.addTargetList(target_list);

    uint32_t level = 0;
    event.getUInt(ParamEnum::task,level);
    task.setLevel(MonitorLevelEnum(level));

    logger->info(boost::format("<control_service> receive start monitor request from %s, request session [%08X] monitor level %d")
                            %sender %event.session %level);

    bool ret = true;
    AppMessage response(AppMessage::message_type::RESPONSE, RequestEnum::start_monitor);
    response.session = event.session;

    if(!task.conatinTarget())
        task.setGlobalMonitor(true);

    switch(MonitorLevelEnum(level))
    {
        case MonitorLevelEnum::server_room:
            ret = false;
        break;
        case MonitorLevelEnum::server_rack:
            ret = false;
        break;
        case MonitorLevelEnum::server:
        {
            for( auto &item : target_list ){
                ret = _config_manager->containsServer(item);
                if(!ret){
                    logger->error(boost::format("<control_service> handleStartMonitorRequest start monitor fail, invalid target server id %s") %item);
                    break;
                }

            }

        }
        break;
        case MonitorLevelEnum::compute_node:
        {
            UUID_TYPE pool_id;
            for( auto &item : target_list ){
                ret = _computepool_manager->searchResource(item,pool_id);
                if(!ret){
                    logger->error(boost::format("<control_service> handleStartMonitorRequest start monitor fail, invalid target compute resource %s") %item);
                    break;
                }

            }

        }
        break;
        case MonitorLevelEnum::host:
        {
            for( auto &item : target_list ){
                ret = _config_manager->containsHost(item);
                if(!ret){
                    logger->error(boost::format("<control_service> handleStartMonitorRequest start monitor fail, invalid target host id %s") %item);
                    break;
                }

            }
        }
        break;
        default:
            ret = false;
        break;
    }

    if(ret){
        if(_monitor_manager->addTask(task))
        {
            response.setUInt(ParamEnum::task, task.getTaskID());
        }else
        {
            ret = false;
        }
    }

    response.success = ret;
    sendMessage(response, sender);
}

void MainService::handleStopMonitorRequest(AppMessage& event, const string& sender)
{
    uint32_t task_id = 0;
    event.getUInt(ParamEnum::task,task_id);

    AppMessage response(AppMessage::message_type::RESPONSE, RequestEnum::stop_monitor);
    response.session = event.session;
    response.success =_monitor_manager->removeTask(task_id);
    sendMessage(response, sender);

    logger->info(boost::format("<control_service> receive stop monitor request from %s, request session [%08X]")
                            %sender %event.session);

}

void MainService::handleStartStatisticRequest(AppMessage& event, const string& sender)
{
    _statistic_server = sender;
    _statistic_timeout = 0;
    statistic_timer_id = setLoopTimer(statistic_interval, statistic_timer_session);

    AppMessage response(AppMessage::message_type::RESPONSE, RequestEnum::query_compute_pool);
    response.session = statistic_timer_session;
    response.success = true;

    sendMessage(response, sender);
    reportStatisticData();
}

void MainService::handleStopStatisticRequest(AppMessage& event, const string& sender)
{
    if(statistic_timer_id != 0)
    {
        AppMessage response(AppMessage::message_type::RESPONSE, RequestEnum::query_compute_pool);
        response.session = statistic_timer_session;
        response.success = true;

        statistic_timer_id = 0;
        _statistic_server = "";
        sendMessage(response, sender);
    }
}

void MainService::handleStatisticKeepAlive()
{
    _statistic_timeout = 0;
}

void MainService::handleMonitorTimeout()
{
    _monitor_manager->checkTimeout();
    vector<Monitor> monitor_list;
    _monitor_manager->getAllMonitor(monitor_list);

   for(auto& monitor : monitor_list)
   {
        if(monitor.hasTarget())
        {
            switch(monitor.getLevel())
            {
                case MonitorLevelEnum::system:
                    notifySystemMonitorData(monitor);
                break;
                case MonitorLevelEnum::server_room:
                    notifyServerRoomMonitorData(monitor);
                break;
                case MonitorLevelEnum::server_rack:
                    notifyServerRackMonitorData(monitor);
                break;
                case MonitorLevelEnum::server:
                    notifyServerMonitorData(monitor);
                break;
                case MonitorLevelEnum::compute_node:
                    notifyComputeNodeMonitorData(monitor);
                break;
                case MonitorLevelEnum::host:
                    notifyHostMonitorData(monitor);
                break;
                default:
                break;
            }
        }
   }
}

void MainService::notifySystemMonitorData(Monitor monitor)
{
    if(!monitor.hasListener()) return;
    AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);
}

void MainService::notifyServerRoomMonitorData(Monitor monitor)
{
    if(!monitor.hasListener()) return;
    AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);

}

void MainService::notifyServerRackMonitorData(Monitor monitor)
{   if(!monitor.hasListener()) return;
    AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);

}

void MainService::notifyServerMonitorData(Monitor monitor)
{
    if(!monitor.hasListener()) return;
    AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);

}

void MainService::notifyHostMonitorData(Monitor monitor)
{
    if(!monitor.hasListener()) return;
    AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);

}

void MainService::notifyComputeNodeMonitorData(Monitor monitor)
{
    if(!monitor.hasListener()) return;

    map<uint32_t,vector<ComputeResource>> dispatch_map;

    for(auto& listener_id : monitor.getListener())
        dispatch_map[listener_id] = move(vector<ComputeResource>());

    for(auto& target_id : monitor.getTargetList())
    {
        UUID_TYPE pool_id;
        if(_computepool_manager->searchResource(target_id.first,pool_id))
        {
            ComputeResource resource;
            if(_computepool_manager->getResource(pool_id,target_id.first,resource))
            {
                 for(auto& item : dispatch_map)
                    dispatch_map[item.first].emplace_back(resource);
            }
        }
    }

    map<UUID_TYPE,ComputePool> compute_pool;
    vector<ComputeResource> resource_list;
    _computepool_manager->queryAllPool(compute_pool);
    for(auto& pool : compute_pool)
    {
        _computepool_manager->queryResource(pool.first,resource_list);
    }

    for(auto& item : dispatch_map)
    {
        for(auto& resource : resource_list)
        {
             dispatch_map[item.first].emplace_back(resource);
        }
    }


    AppMessage::string_array_type name;
    AppMessage::uint_array_type number;
    AppMessage::uint_array_type cpu_count;
    AppMessage::float_array_type cpu_usage;
    AppMessage::uint_array_array_type memory;
    AppMessage::float_array_type memory_usage;
    AppMessage::uint_array_array_type disk_volume;
    AppMessage::float_array_type disk_usage;
    AppMessage::uint_array_array_type disk_io;
    AppMessage::uint_array_array_type network_io;
    AppMessage::uint_array_array_type speed;
    AppMessage::string_array_type timestamp;
    AppMessage::uint_array_type status_list;

    AppMessage::uint_array_type tmp_num;

    MonitorTask task;
    ServerStatus status;
    for(auto& item : dispatch_map)
    {

        if(_monitor_manager->getTask(item.first,task))
        {
            AppMessage event(AppMessage::message_type::RESPONSE, EventEnum::monitor_data);
            event.success = true;
            event.session = task.getReceivedSession();
            event.setUInt(ParamEnum::task, task.getTaskID());
            event.setUInt(ParamEnum::level, uint32_t(task.getLevel()));


            name.clear();
            number.clear();
            cpu_count.clear();
            cpu_usage.clear();
            memory.clear();
            memory_usage.clear();
            disk_volume.clear();
            disk_usage.clear();
            disk_io.clear();
            network_io.clear();
            speed.clear();
            timestamp.clear();
            status_list.clear();

            for(auto& resource : item.second)
            {
                if(_status_manager->getServerStatus(resource.getServerUUID(),status))
                {
                    name.emplace_back(resource.getName());
                    number.emplace_back(resource.getHostSize());
                    cpu_count.emplace_back(status.getCounter().getCpuCounter().getCpuCount());
                    cpu_usage.emplace_back(status.getCounter().getCpuCounter().getCpuUsage());

                    status.getCounter().getMemoryCounter().transfertoArray(tmp_num);
                    memory.emplace_back(tmp_num);
                    memory_usage.emplace_back(status.getCounter().getMemoryUsage());


                    status.getCounter().getDiskCounter().transfertoArray(tmp_num);
                    disk_volume.emplace_back(tmp_num);
                    disk_usage.emplace_back(status.getCounter().getDiskUsage());

                    status.getCounter().getDiskIOCounter().transfertoArray(tmp_num);
                    disk_io.emplace_back(tmp_num);

                    status.getCounter().getNetworkCounter().transfertoArray(tmp_num);
                    network_io.emplace_back(tmp_num);

                    status.getCounter().getSpeedCounter().transfertoArray(tmp_num);
                    speed.emplace_back(tmp_num);

                    timestamp.emplace_back(status.getCounter().getTimeStamp());
                    status_list.emplace_back(uint64_t(status.getCounter().getStatus()));
                }

            }
            sendMessage(event, task.getReceivedNode());
        }

    }





}

void MainService::handleStatisticCheckTimeout()
{
}

void MainService::handleSynchronizeTimeout()
{
}

void MainService::handleStorageServerSyncTimeout()
{
    lock_type lock(_storage_server_mutex);
}

void MainService::onStatusCheckTimeout()
{
}

void MainService::reportStatisticData()
{
}

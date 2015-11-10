#include "main_service.h"

#include <boost/filesystem.hpp>
#include <exception>


using namespace zhicloud;
using namespace zhicloud::control_server;

const string MainService::version("2.1#20151030-1");
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



MainService::MainService(const string& service_name, const string& domain, const string& ip, const string& group_ip, const uint16_t& group_port, const string& server,
        const string& rack, const string& server_name):
    NodeService(ServiceType::control_server, service_name, domain, ip, (5600+(uint32_t)ServiceType::control_server), 200, group_ip, group_port, version, server, rack, server_name)
{
    stringstream ss;
    ss << config_root << "resource/";
    const string data_source = ss.str();

    if(! boost::filesystem::exists(data_source))
        boost::filesystem::create_directory(data_source);

    logger = getLogger("MainService");
    _compute_pool_manager =  boost::shared_ptr<ComputePoolManager>(new ComputePoolManager(data_source,service_name));

    this->initialize();
    logger->info("<ControlService>main service start success.");
}

MainService::~MainService() {}

bool MainService::initialize()
{
    console(boost::format("<ControlService>%s initilized")
            %fullname);
    logger->info(boost::format("<ControlService>%s initilized")
            %fullname);

    if(!_compute_pool_manager->load())
        return false;

    return true;
}

bool MainService::onStart()
{

    if(! NodeService::onStart())
        return false;

    monitor_timer_id = setLoopTimer(monitor_interval, monitor_timer_session);
    status_timer_id = setLoopTimer(status_interval, status_timer_session);
    statistic_timer_id = setLoopTimer(statistic_interval, statistic_timer_session);
    synchronize_timer_id = setLoopTimer(synchronize_interval, synchronize_timer_session);
    storage_server_timer_id = setLoopTimer(storage_server_interval, storage_server_timer_session);

    return true;
}

void MainService::onStop()
{

    clearTimer(monitor_timer_id);
    clearTimer(status_timer_id);
    clearTimer(statistic_timer_id);
    clearTimer(synchronize_timer_id);
    clearTimer(storage_server_timer_id);
}

void MainService::onChannelConnected(const string& node_name, const ServiceType& node_type, const string& remote_ip, const uint16_t& remote_port)
{
    logger->info(boost::format("<ControlService>channel connected, node name '%s', type: %d")
            %node_name %(uint32_t)node_type);
    //can from node_client,data_server,storage_server,intelligent_router,data_index
}

void MainService::onChannelDisconnected(const string& node_name, const ServiceType& node_type)
{
    logger->info(boost::format("<ControlService>channel disconnected, node name '%s', type: %d")
            %node_name %(uint32_t)node_type);
}

void MainService::handleEventMessage(AppMessage& event, const string& sender)
{
}

void MainService::handleRequestMessage(AppMessage& request,const string& sender)
{
}


void MainService::handleResponseMessage(AppMessage& response,const string& sender)
{
}

void MainService::onTransportEstablished(const string& ip, const uint16_t& port)
{
}

void MainService::handleTimeout(AppMessage& event, const string& sender)
{
}

void MainService::handleNotifyTimeout()
{
}


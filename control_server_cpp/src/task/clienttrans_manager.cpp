#include "clienttrans_manager.h"
#include "query_computepool.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;
using namespace transaction;

const uint32_t ClientTransManager::session_count(100);

ClientTransManager::ClientTransManager(NodeService* messsage_handler,
    ComputePoolManager& computepool_manager,
    StatusManager& status_manager,
    ConfigManager& config_manager,
    ServiceManager& service_manager,
    ExpireManager& expire_manager,
    const uint32_t& work_thread):
    BaseManager< BaseTask< TaskSession, NodeService > >(session_count, work_thread),
    _computepool_manager(computepool_manager),
    _status_manager(status_manager),
   _config_manager(config_manager),
   _service_manager(service_manager),
  _expire_manager(expire_manager)
{

    //ctor
    addTask(new QueryComputePoolTask(messsage_handler,
            _computepool_manager,_status_manager));


}

ClientTransManager::~ClientTransManager()
{
    //dtor
}

#include "clienttrans_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

const uint32_t ClientTransManager::session_count(100);

ClientTransManager::ClientTransManager(NodeService* messsage_handler,
    ComputePoolManager& computepool_manager,
    const uint32_t& work_thread):
    BaseManager(session_count, work_thread),
    _computepool_manager(computepool_manager)
{
    //ctor
}

ClientTransManager::~ClientTransManager()
{
    //dtor
}

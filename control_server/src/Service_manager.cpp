#include "Service_manager.h"


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

#include "Port_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

PortManager::PortManager(const string& resource_path,const string& logger_name):_modified(false)
{
    _logger = getLogger(logger_name);
}

PortManager::~PortManager()
{
    //dtor
}

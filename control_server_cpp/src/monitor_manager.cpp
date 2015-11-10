#include "monitor_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;
const uint32_t MonitorManager::_max_timeout(5);


MonitorManager::MonitorManager(const string& logger_name)
{
     _logger = getLogger(logger_name);
}

MonitorManager::~MonitorManager()
{
    //dtor
}

#include "Forwarder_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

ForwarderManager::ForwarderManager(const string& resource_path,const string& logger_name):_modified(false),_crc(0)
{
     _logger = getLogger(logger_name);
}

ForwarderManager::~ForwarderManager()
{
    //dtor
}

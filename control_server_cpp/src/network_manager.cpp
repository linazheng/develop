#include "network_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;


NetworkManager::NetworkManager(const string& resource_path,const string& logger_name):_is_sorted(true)
{
     _logger = getLogger(logger_name);
}

NetworkManager::~NetworkManager()
{
    //dtor
}

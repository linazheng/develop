#include "config_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

ConfigManager::ConfigManager(const string &logger_name)
{
     _logger = getLogger(logger_name);
}

ConfigManager::~ConfigManager()
{

}

bool ConfigManager::containsHost(const UUID_TYPE& host)
{
    return false;
}

bool ConfigManager::containsServer(const UUID_TYPE& server)
{
    return false;
}

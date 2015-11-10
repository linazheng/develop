#include "status_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

StatusManager::StatusManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

StatusManager::~StatusManager()
{
    //dtor
}

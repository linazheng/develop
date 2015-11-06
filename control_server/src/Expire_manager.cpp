#include "Expire_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;


const uint32_t ExpireManager::_tresource_type_host(0);

ExpireManager::ExpireManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

ExpireManager::~ExpireManager()
{
    //dtor
}

#include "Storage_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

StorageManager::StorageManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

StorageManager::~StorageManager()
{
    //dtor
}

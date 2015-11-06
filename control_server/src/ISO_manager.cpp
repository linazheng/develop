#include "ISO_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;


ISOManager::ISOManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

ISOManager::~ISOManager()
{
    //dtor
}

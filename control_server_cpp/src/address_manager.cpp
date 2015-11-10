#include "address_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;



AddressManager::AddressManager(const string& resource_path,const string& logger_name):_modified(false)
{
     _logger = getLogger(logger_name);
}

AddressManager::~AddressManager()
{

}

#include "ComputePool_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

ComputePoolManager::ComputePoolManager(const string& resource_path,const string& logger_name)
{
      _logger = getLogger(logger_name);
}

ComputePoolManager::~ComputePoolManager()
{

}

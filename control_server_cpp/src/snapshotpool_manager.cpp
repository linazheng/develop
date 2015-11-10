#include "snapshotpool_manager.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

SnapshotPoolManager::SnapshotPoolManager(const string& logger_name)
{
      _logger = getLogger(logger_name);
}

SnapshotPoolManager::~SnapshotPoolManager()
{
    //dtor
}

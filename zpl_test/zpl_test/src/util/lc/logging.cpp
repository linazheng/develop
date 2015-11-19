#include <iostream>
#include <sstream>
#include <boost/make_shared.hpp>
#include <boost/filesystem.hpp>
#include <util/lc/logging.h>
#include <util/lc/logger.h>
#include <util/lc/logger_manager.h>

using namespace boost::filesystem;

namespace zhicloud {
namespace util {
namespace lc {

bool initialLogging()
{
    return LoggerManager::instance()->initialLogging();
}

bool finishLogging()
{
    return LoggerManager::instance()->finishLogging();
}

bool addFileAppender(const string& path_name, const string& prefix, const uint64_t& max_size)
{
    return LoggerManager::instance()->addAsyncFileAppender("zhicloud_root", path_name, prefix, max_size);
}

bool addSyncFileAppender(const string& path_name, const string& prefix, const uint64_t& max_size)
{
    return LoggerManager::instance()->addSyncFileAppender("zhicloud_root", path_name, prefix, max_size);
}

bool setCollector(const string& path_name, const uint64_t& max_size)
{
    return LoggerManager::instance()->setCollector(path_name, max_size);
}

boost::shared_ptr<Logger> getLogger(const string& name, const log_level& level)
{
    return LoggerManager::instance()->getLogger(name, level);
}

}
}
}

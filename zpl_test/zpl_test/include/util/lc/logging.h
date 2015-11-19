#ifndef NEW_LOGGING_H
#define NEW_LOGGING_H
#include <string>
#include <boost/shared_ptr.hpp>
#include "logger.h"

using namespace std;
namespace zhicloud {
namespace util {
namespace lc {

typedef boost::shared_ptr<Logger> logger_type;
bool initialLogging();
bool finishLogging();
bool addFileAppender(const string& path_name, const string& prefix, const uint64_t& max_size);
bool addSyncFileAppender(const string& path_name, const string& prefix, const uint64_t& max_size);
bool setCollector(const string& path_name, const uint64_t& max_size);
logger_type getLogger(const string& name, const log_level& level = level_info);

}
}
}

#endif // LOGGING_H

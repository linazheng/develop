#include <util/lc/async_appender.h>
#include <util/lc/logger_manager.h>

namespace zhicloud {
namespace util {
namespace lc {

AsyncAppender::AsyncAppender(const std::string &name) : Appender(name)
{
}

void AsyncAppender::doAppend(const LoggingEvent &event)
{
    LoggerManager::instance()->pushAsyncEvent(std::make_pair(event, shared_from_this()));
}

}
}
}

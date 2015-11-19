#ifndef ASYNC_APPENDER_H
#define ASYNC_APPENDER_H

#include <util/lc/appender.h>
#include <util/lc/block_queue.hpp>
#include <utility>

namespace zhicloud {
namespace util {
namespace lc {

class AsyncAppender : public Appender, public std::enable_shared_from_this<AsyncAppender>
{
public:
    AsyncAppender(const std::string &name);
    virtual ~AsyncAppender() = default;
    virtual void doAppend(const LoggingEvent &event) override final;
    virtual void doAsyncAppend(const LoggingEvent &event) = 0;
};

}
}
}

#endif // APPENDER_h

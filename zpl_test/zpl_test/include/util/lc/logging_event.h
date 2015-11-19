#ifndef LOGGING_EVENT_H
#define LOGGING_EVENT_H

#include <string>
#include <util/logger.h>
#include <util/lc/logging_time.h>

namespace zhicloud {
namespace util {
namespace lc {

class LoggingEvent
{
public:
    enum class EVENT_TYPE
    {
        NORMAL,
        STOP
    };

    LoggingEvent() = default;

    LoggingEvent(const std::string &level, const LoggingTime &time, const std::string &logger_name, const std::string &message)
    {
        m_level = level;
        m_time = time;
        m_logger_name = logger_name;
        m_message = message;
    }

    const std::string& level()const
    {
        return m_level;
    }

    const LoggingTime& time() const
    {
        return m_time;
    }

    const std::string& logger_name() const
    {
        return m_logger_name;
    }

    const std::string& message() const
    {
        return m_message;
    }

    EVENT_TYPE eventType() const
    {
        return m_event_type;
    }

    void eventType(EVENT_TYPE event_type)
    {
        m_event_type = event_type;
    }

private:
    std::string m_level;
    LoggingTime m_time;
    std::string m_logger_name;
    std::string m_message;
    EVENT_TYPE m_event_type = EVENT_TYPE::NORMAL;
};

}
}
}

#endif // LOGGING_EVENT_H

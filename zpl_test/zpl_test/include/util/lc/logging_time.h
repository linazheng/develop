#ifndef LOGGING_TIME_H
#define LOGGING_TIME_H


namespace zhicloud {
namespace util {
namespace lc {

class LoggingTime
{
public:
    LoggingTime() = default;

    LoggingTime(uint32_t year, uint32_t month, uint32_t day, uint32_t hour, uint32_t minute, uint32_t second, uint32_t usecond)
    {
        m_year = year;
        m_month = month;
        m_day = day;
        m_hour = hour;
        m_minute = minute;
        m_second = second;
        m_usecond = usecond;
    }

    uint32_t year() const
    {
        return m_year;
    }

    uint32_t month() const
    {
        return m_month;
    }

    uint32_t day() const
    {
        return m_day;
    }

    uint32_t hour() const
    {
        return m_hour;
    }

    uint32_t minute() const
    {
        return m_minute;
    }

    uint32_t second() const
    {
        return m_second;
    }

    uint32_t usecond() const
    {
        return m_usecond;
    }

private:
    uint32_t m_year;
    uint32_t m_month;
    uint32_t m_day;
    uint32_t m_hour;
    uint32_t m_minute;
    uint32_t m_second;
    uint32_t m_usecond;
};

}
}
}

#endif // LOGGING_TIME_H

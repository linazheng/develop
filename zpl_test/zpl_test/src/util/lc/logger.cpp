#include <boost/make_shared.hpp>
#include <util/lc/logger.h>
#include <util/lc/logger_manager.h>
#include <boost/filesystem.hpp>
#include <sys/time.h>
#include <sstream>
#include <cstdio>

namespace zhicloud {
namespace util {
namespace lc {

Logger::Logger(const string& name, const log_level& level)
{
    this->m_name = name;
    m_level = level;
}

Logger::~Logger()
{
    //dtor
}

void Logger::log_impl(const string &level_str, const string &message)
{
    struct timeval _tv;
    gettimeofday(&_tv, NULL);
    struct tm _tm;
    localtime_r(&_tv.tv_sec, &_tm);
    uint32_t now_year = 1900 + _tm.tm_year;
    uint32_t now_month = 1 + _tm.tm_mon;
    uint32_t now_day = _tm.tm_mday;
    LoggerManager::instance()->log(LoggingEvent(level_str, LoggingTime(now_year, now_month, now_day, _tm.tm_hour, \
                                                                        _tm.tm_min, _tm.tm_sec, _tv.tv_usec), m_name, message));
}

void Logger::debug(const string& content)
{
    if(m_level <= level_debug)
    {
        log_impl("[DEBUG]", content);
    }
}

void Logger::info(const string& content)
{
    if(m_level <= level_info)
    {
        log_impl("[INFO]", content);
    }
}

void Logger::warn(const string& content)
{
    if(m_level <= level_warning)
    {
        log_impl("[WARNING]", content);
    }
}

void Logger::error(const string& content)
{
    if(m_level <= level_error)
    {
        log_impl("[ERROR]", content);
    }
}

void Logger::fatal(const string& content)
{
    if(m_level <= level_fatal)
    {
        log_impl("[FATAL]", content);
    }
}

void Logger::debug(boost::format& input)
{
    if(m_level <= level_debug)
    {
        log_impl("[DEBUG]", input.str());
    }
}

void Logger::info(boost::format& input)
{
    if(m_level <= level_info)
    {
        log_impl("[INFO]", input.str());
    }
}

void Logger::warn(boost::format& input)
{
    if(m_level <= level_warning)
    {
        log_impl("[WARNING]", input.str());
    }
}

void Logger::error(boost::format& input)
{
    if(m_level <= level_error)
    {
        log_impl("[ERROR]", input.str());
    }
}

void Logger::fatal(boost::format& input)
{
    if(m_level <= level_fatal)
    {
        log_impl("[FATAL]", input.str());
    }
}

void Logger::hex(const log_level& level, const string& input)
{
    hex(level, input.c_str(), input.length());
}

void Logger::hex(const log_level& level, const char* buf, const int& buf_length)
{
    if(m_level <= level)
    {
        string level_str;
        if(level == level_debug)
        {
            level_str = "[DEBUG]";
        }
        else if(level == level_warning)
        {
            level_str = "[WARNING]";
        }
        else if(level == level_error)
        {
            level_str = "[ERROR]";
        }
        else if(level == level_fatal)
        {
            level_str = "[FATAL]";
        }
        else
        {
            level_str = "[INFO]";
        }

        ostringstream ost;
        for(int offset = 0; offset < buf_length; offset++)
        {
            uint8_t value = (uint8_t) buf[offset];
            ost << std::uppercase << std::hex << (value >> 4) << (value&0x0F);
            if(offset != (buf_length - 1))
            {
                ost << " ";
            }
        }

        log_impl(level_str, ost.str());
    }
}

}
}
}

#include <util/lc/logger_manager.h>
#include <iostream>
#include <sstream>
#include <boost/make_shared.hpp>
#include <boost/filesystem.hpp>
#include <util/lc/logger_manager.h>
#include <util/lc/async_file_appender.h>
#include <util/lc/file_appender.h>

using namespace boost::filesystem;

namespace zhicloud {
namespace util {
namespace lc {

bool LoggerManager::delPathTailSlash(const std::string &path, std::string &new_path)
{
    if(path.empty())
    {
        return false;
    }

    uint16_t length = path.length();

    if(path[length - 1] == '/')
    {
        new_path = path.substr(0, length - 1);
        if(new_path.empty())
        {
            return false;
        }
    }
    else
    {
        new_path = path;
    }

    return true;
}

bool LoggerManager::addAsyncFileAppender(const std::string &appender_name, const std::string& _path, const string& prefix, const uint64_t& max_size)
{
    std::string new_path;
    if(!delPathTailSlash(_path, new_path)) {
        return false;
    }

    path log_path(new_path);
    if(!exists(log_path))
    {
        if(!create_directory(log_path)) {
            return false;
        }
    }

    auto iter = m_appender_path_infos.find(new_path);
    if(iter != m_appender_path_infos.end()) {
        return false; //already exist appender with same path
    }

    std::shared_ptr<Appender> appender;

    if(appender_name == "zhicloud_root")
    {
        appender = std::make_shared<AsyncFileAppender>(appender_name, _path, prefix, max_size);
        m_root_appenders.push_back(appender);
        auto iter = m_collector_infos.find(new_path);

        if(iter != m_collector_infos.end()) {
            appender->setCollector(iter->second);
        }
    }
    else
    {
        //////////////////
        //to do in future
        /////////////////
    }

    m_appender_path_infos[new_path] = appender;

    return true;
}

bool LoggerManager::addSyncFileAppender(const std::string &appender_name, const std::string& _path, const string& prefix, const uint64_t& max_size)
{
    std::string new_path;
    if(!delPathTailSlash(_path, new_path)) {
        return false;
    }

    path log_path(new_path);
    if(!exists(log_path))
    {
        if(!create_directory(log_path)) {
            return false;
        }
    }

    auto iter = m_appender_path_infos.find(new_path);
    if(iter != m_appender_path_infos.end()) {
        return false; //already exist appender with same path
    }

    std::shared_ptr<Appender> appender;

    if(appender_name == "zhicloud_root")
    {
        appender = std::make_shared<FileAppender>(appender_name, _path, prefix, max_size);
        m_root_appenders.push_back(appender);
        auto iter = m_collector_infos.find(new_path);

        if(iter != m_collector_infos.end()) {
            appender->setCollector(iter->second);
        }
    }
    else
    {
        //////////////////
        //to do in future
        /////////////////
    }

    m_appender_path_infos[new_path] = appender;

    return true;
}

void LoggerManager::runAsync()
{
    while(true)
    {
        std::pair<LoggingEvent, std::shared_ptr<AsyncAppender>> async_event;
        m_async_events.get(async_event);
        const LoggingEvent &event = async_event.first;

        if(event.eventType() == LoggingEvent::EVENT_TYPE::STOP)
        {
            break;
        }

        const std::shared_ptr<AsyncAppender> &async_appender = async_event.second;
        async_appender->doAsyncAppend(event);
    }
}

bool LoggerManager::initialLogging()
{
    std::thread tmp(&LoggerManager::runAsync, this);
    m_async_thread = std::move(tmp);

    return true;
}

bool LoggerManager::finishLogging()
{
    LoggingEvent event;
    event.eventType(LoggingEvent::EVENT_TYPE::STOP);
    std::shared_ptr<AsyncAppender> async_appender;
    pushAsyncEvent(std::make_pair(event, async_appender));
    m_async_thread.join();

    return true;
}

bool LoggerManager::setCollector(const std::string& path, const uint64_t& max_size)
{
    std::string new_path;
    if(!delPathTailSlash(path, new_path))
    {
        return false;
    }

    if(m_collector_infos.find(new_path) != m_collector_infos.end()) {
        return false; //alread exist collector with same path
    }

    auto iter = m_appender_path_infos.find(new_path);

    if(iter != m_appender_path_infos.end()) {
        auto appender = iter->second;
        appender->setCollector(max_size);
    }

    m_collector_infos[new_path] = max_size;

    return true;
}

void LoggerManager::pushAsyncEvent(const std::pair<LoggingEvent, shared_ptr<AsyncAppender>> &async_event)
{
    m_async_events.put(async_event);
}

logger_type LoggerManager::getLogger(const std::string& name, const log_level& level)
{
    return boost::make_shared<Logger>(name, level);
}

std::shared_ptr<Appender> LoggerManager::findLatestAppender(const std::string &logger_name)
{
    std::shared_ptr<Appender> latest_appender;
    //////////////////////
    //to do in future
    //////////////////////
    return latest_appender;
}

void LoggerManager::log(const LoggingEvent &event)
{
    auto latest_appender = findLatestAppender(event.logger_name());
    if(latest_appender) {
        latest_appender->append(event);
    }

    for(auto appender : m_root_appenders)
    {
        appender->append(event);
    }
}

}
}
}

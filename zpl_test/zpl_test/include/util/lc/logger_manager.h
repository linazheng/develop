#ifndef LOGGER_MANAGER_H
#define LOGGER_MANAGER_H

#include <util/lc/singleton.h>
#include <util/lc/logging.h>
#include <util/lc/async_appender.h>
#include <unordered_map>
#include <thread>
#include <service/passive_queue.hpp>

namespace zhicloud {
namespace util {
namespace lc {

class LoggerManager : public Singleton<LoggerManager>
{
public:
    bool initialLogging();
    bool finishLogging();
    bool addAsyncFileAppender(const std::string &appender_name, const std::string& path, const std::string& prefix, const uint64_t& max_size);
    bool addSyncFileAppender(const std::string &appender_name, const std::string& path, const std::string& prefix, const uint64_t& max_size);
    bool setCollector(const std::string& path, const uint64_t& max_size);
    logger_type getLogger(const std::string& name, const log_level& level = level_info);
    void log(const LoggingEvent &event);
    void pushAsyncEvent(const std::pair<LoggingEvent, shared_ptr<AsyncAppender>> &async_event);

private:
    void runAsync();
    std::shared_ptr<Appender> findLatestAppender(const std::string &logger_name);
    bool delPathTailSlash(const std::string &path, std::string &new_path);
    std::vector<std::shared_ptr<Appender>> m_root_appenders;
    std::unordered_map<std::string, std::shared_ptr<Appender>> m_appenders;
    std::unordered_map<std::string, std::shared_ptr<Appender>> m_appender_path_infos;
    std::unordered_map<std::string, uint64_t> m_collector_infos;
//    BlockQueue<std::pair<LoggingEvent, std::shared_ptr<AsyncAppender>>> m_async_events;
    zhicloud::service::PassiveQueue<std::pair<LoggingEvent, std::shared_ptr<AsyncAppender>>, 8192> m_async_events;
    std::thread m_async_thread;
};

}
}
}

#endif // LOGGER_MANAGER_H

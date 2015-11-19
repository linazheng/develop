#ifndef FILE_APPENDER_H
#define FILE_APPENDER_H

#include <util/lc/appender.h>
#include <mutex>
#include <queue>
#include <fstream>

namespace zhicloud {
namespace util {
namespace lc {

class FileAppender : public Appender
{
public:
    FileAppender(const std::string &name, const std::string &path, const std::string &prefix, uint64_t size);
    virtual ~FileAppender();
    virtual void doAppend(const LoggingEvent &event) override;

private:
    std::string m_path;
    std::string m_prefix;
    uint64_t m_file_size = 0;
    std::fstream m_stream;
    std::mutex m_mutex;
    std::queue<pair<std::string, uint64_t>> m_file_infos;
    uint32_t m_year = 0;
    uint32_t m_month = 0;
    uint32_t m_day = 0;
    uint32_t m_seq = 0;
    uint32_t m_cur_file_size = 0;
    uint32_t m_all_file_size = 0;
    std::string m_cur_file_name;
};

}
}
}

#endif

#include <util/lc/async_file_appender.h>
#include <boost/filesystem.hpp>
#include <sstream>

namespace zhicloud {
namespace util {
namespace lc {

AsyncFileAppender::AsyncFileAppender(const std::string &name, const std::string &path, const std::string &prefix, uint64_t size) : AsyncAppender(name)
{
    m_path = path;
    m_prefix = prefix;
    m_file_size = size;
}

AsyncFileAppender::~AsyncFileAppender()
{
    m_stream.close();
}

void AsyncFileAppender::doAsyncAppend(const LoggingEvent &event)
{
    const LoggingTime &time = event.time();
    uint32_t year = time.year();
    uint32_t month = time.month();
    uint32_t day = time.day();
    uint32_t hour = time.hour();
    uint32_t minute = time.minute();
    uint32_t second = time.second();
    uint32_t usecond = time.usecond();
    std::string time_str = (boost::format("%d-%02d-%02d %02d:%02d:%02d.%06ld") % year % month % day \
                       % hour % minute % second % usecond).str();
    std::string file_name = (boost::format("%s/%s_%d%02d%02d_") % m_path % m_prefix % year \
                            % month % day).str();
    ostringstream ost;
    ost << time_str << " " << event.level() << " " << event.message();
    std::string log_message = ost.str();

    if(m_year != year || m_month != month || m_day != day || (m_file_size > 0 && m_cur_file_size > m_file_size))
    {
        if(m_year != 0)
        {
            m_file_infos.push(make_pair(m_cur_file_name, m_cur_file_size));
            m_stream.close();
        }

        ostringstream ost;
        ost << file_name << m_seq++ << ".log";
        m_cur_file_name = ost.str();
        m_stream.open(m_cur_file_name, ios_base::out);
        m_cur_file_size = 0;
        m_year = year;
        m_month = month;
        m_day = day;
    }

    if(m_collector_size > 0 && m_all_file_size > m_collector_size)
    {
        if(!m_file_infos.empty())
        {
            std::pair<string, uint32_t> file_info = m_file_infos.front();
            m_file_infos.pop();
            boost::filesystem::path file_path(file_info.first);
            boost::filesystem::remove(file_path);
            m_all_file_size -= file_info.second;
        }
    }

    m_stream << log_message << endl;
    uint32_t message_size = log_message.size() + 1;
    m_cur_file_size += message_size;
    m_all_file_size += message_size;
}

}
}
}

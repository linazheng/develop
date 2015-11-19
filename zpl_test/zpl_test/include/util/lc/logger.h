#ifndef NEW_LOGGER_H
#define NEW_LOGGER_H
#include <boost/log/sources/severity_logger.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/format.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <string>

using namespace std;

namespace zhicloud {
namespace util {
namespace lc {

enum log_level
{
    level_debug,
    level_info,
    level_warning,
    level_error,
    level_fatal
};

class Logger
{
public:
    Logger(const string& name, const log_level& level = level_info);
    virtual ~Logger();
    void debug(const string& content);
    void info(const string& content);
    void warn(const string& content);
    void error(const string& content);
    void fatal(const string& content);
    void debug(boost::format& input);
    void info(boost::format& input);
    void warn(boost::format& input);
    void error(boost::format& input);
    void fatal(boost::format& input);
    void hex(const log_level& level, const string& input);
    void hex(const log_level& level, const char* buf, const int& buf_length);

private:
    void log_impl(const string &level_str, const string &message);
    string m_name;
    log_level m_level;
};

}
}
}

#endif

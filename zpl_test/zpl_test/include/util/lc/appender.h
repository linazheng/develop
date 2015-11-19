#ifndef APPENDER_H
#define APPENDER_H

#include <string>
#include <memory>
#include <util/lc/logging_event.h>

namespace zhicloud {
namespace util {
namespace lc {

class Appender
{
public:
    Appender(const std::string &name);
    virtual ~Appender() = default;
    void append(const LoggingEvent &event);
    virtual void doAppend(const LoggingEvent &event) = 0;
    const std::string& name() const;
    void parent(std::shared_ptr<Appender> &_parent);
    void setCollector(uint64_t size);

protected:
    std::shared_ptr<Appender> m_parent;
    std::string m_name;
    uint64_t m_collector_size = 0;
};

}
}
}

#endif // APPENDER_h

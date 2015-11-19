#include <util/lc/appender.h>

namespace zhicloud {
namespace util {
namespace lc {

Appender::Appender(const std::string &name)
{
    m_name = name;
}

const std::string& Appender::name() const
{
    return m_name;
}

void Appender::setCollector(uint64_t size)
{
    m_collector_size = size;
}

void Appender::append(const LoggingEvent &event)
{
    doAppend(event);

    if(m_parent) {
        m_parent->append(event);
    }
}

void Appender::parent(std::shared_ptr<Appender> &_parent)
{
    m_parent = _parent;
}

}
}
}

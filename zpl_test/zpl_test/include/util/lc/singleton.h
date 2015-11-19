#ifndef SINGLETON_H
#define SINGLETON_H

#include <memory>
#include <mutex>
#include <atomic>

namespace zhicloud {
namespace util {
namespace lc {

template<typename T>
class Singleton
{
public:
    static std::shared_ptr<T> instance()
    {
        if(!m_instance_ready.load())
        {
            std::lock_guard<std::mutex> guard(m_mutex);

            if(!m_instance_ready.load()) //double check (DCLP)
            {
                m_instance = std::make_shared<T>();
                m_instance_ready.store(true);
            }
        }

        return m_instance;
    }

protected:
    virtual ~Singleton() = default;
    Singleton() = default;
    Singleton(const Singleton &) = delete;

private:
    static std::shared_ptr<T> m_instance;
    static std::atomic<bool> m_instance_ready;
    static std::mutex m_mutex;
};

template<typename T>
std::shared_ptr<T> Singleton<T>::m_instance;

template<typename T>
std::atomic<bool> Singleton<T>::m_instance_ready(false);

template<typename T>
std::mutex Singleton<T>::m_mutex;

}
}
}

#endif

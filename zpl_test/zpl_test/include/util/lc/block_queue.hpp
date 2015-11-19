#ifndef BLOCK_QUEUE
#define BLOCK_QUEUE

#include <mutex>
#include <deque>
#include <condition_variable>

namespace zhicloud {
namespace util {
namespace lc {

template<typename T>
class BlockQueue
{
public:
    void push(T element)
    {
        std::unique_lock<std::mutex> locker(m_mutex);
        bool empty = m_queue.empty();
        m_queue.push_back(element);

        if(empty)
        {
            locker.unlock();
            m_cond.notify_one();
        }
    }

    T pop()
    {
        std::unique_lock<std::mutex> locker(m_mutex);
        m_cond.wait(locker, [&]{return !m_queue.empty();});
        T element = m_queue.front();
        m_queue.pop_front();

        return element;
    }

    std::deque<T> m_queue;
    std::mutex m_mutex;
    std::condition_variable m_cond;
};

}
}
}

#endif // BLOCK_QUEUE


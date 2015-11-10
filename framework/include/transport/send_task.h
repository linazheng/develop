#ifndef SENDTASK_H
#define SENDTASK_H

#include <string>
#include <mutex>
#include <transport/endpoint_address.hpp>

using std::string;

namespace zhicloud{
    namespace transport{
        class SendTask
        {
            public:
                typedef uint16_t task_id_type;
                typedef EndpointAddress address_type;
                SendTask(const task_id_type& id = 0, const size_t& timeout = 0, const size_t& retry = 0);
                virtual ~SendTask();
                bool allocate();
                bool store(const string& content, const address_type& address);
                void deallocate();
                bool fetch(string& packet, address_type& address);
                const task_id_type& getTaskID() const;
                SendTask(SendTask&& other);
                //return:is_fail, is_timeout
                std::pair< bool, bool > check();
            private:
                task_id_type task_id;
                string _data;
                address_type _address;
                std::mutex mutex;
                typedef std::lock_guard< std::mutex > lock_type;
                bool _allocated;
                size_t _timeout;
                size_t _max_timeout;
                size_t _retry;
                size_t _max_retry;

        };
    }
}




#endif // SENDTASK_H

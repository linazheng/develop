#ifndef TASKMANAGER_H
#define TASKMANAGER_H

#include <list>
#include <map>
#include <mutex>
#include <thread>
#include <util/copyable_atomic.hpp>
#include <transport/send_task.h>

using namespace std;
using zhicloud::util::CopyableAtomic;

namespace zhicloud{
    namespace transport{
        class TaskManager
        {
            public:
                typedef SendTask::task_id_type task_id_type;
                typedef SendTask::address_type address_type;
                TaskManager(const task_id_type& max_capacity = 0xFFFF);
                virtual ~TaskManager();
                bool allocate(task_id_type& task_id);
                bool store(const task_id_type& task_id, const address_type& endpoint, const string& packet_data);
                bool deallocate(const list<task_id_type>& task_list);
                bool fetch(const list<task_id_type>& id_list, list< std::pair< address_type, string > >& request_list);
                bool fetch(const task_id_type& task_id, address_type& endpoint, string& packet_data);
                /** \brief
                 *
                 * \param list of timeout task id
                 * \param list of fail task id
                 * \return false:has timeout or fail task
                 *
                 */
                bool check(list<task_id_type>& timeout_list, list<task_id_type>& failed_list);
            private:
                static const unsigned int default_timeout;
                static const unsigned int max_retry;
                map<task_id_type, SendTask > task_map;
                map<task_id_type, CopyableAtomic< bool > > allocated_map;
                task_id_type max_task;
                task_id_type last_task_id;
        };

    }
}


#endif // TASKMANAGER_H

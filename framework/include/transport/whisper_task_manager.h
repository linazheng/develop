#ifndef WHISPER_TASK_MANAGER_H
#define WHISPER_TASK_MANAGER_H

#include <map>
#include <memory>
#include <atomic>
#include <service/runable.hpp>
#include <service/active_queue.hpp>
#include <util/copyable_atomic.hpp>
#include <util/logging.h>
#include <transport/whisper_session.h>
#include <transport/whisper_task.h>
#include <transport/whisper_rule.h>

using std::map;
using std::unique_ptr;

namespace zhicloud{
    namespace transport{
        class WhisperTaskManager: public zhicloud::service::Runable
        {
            public:
                typedef WhisperSession::session_id_type session_id_type;
                WhisperTaskManager(const session_id_type& session_count, const uint32_t& queue_count);
                virtual ~WhisperTaskManager();
                template < class T >
                void bindObserver(T* t){
                    for(auto& item:_task_map){
                        item.second->bindHandler(t);
                    }
                }

                template < class T >
                void bindService(T* t){
                    for(auto& item:_task_map){
                        item.second->bindFunction(t);
                    }
                }

                bool startTransaction(const WhisperSession::TaskTypeEnum& task_id, AppMessage& msg, session_id_type& session_id);
                void terminateTransaction(const session_id_type& session_id);
                bool processMessage(const session_id_type& session_id, AppMessage& msg);
                bool containsTransaction(const session_id_type& session_id);
            protected:
                virtual bool onStart();
                virtual void onStopping();
            private:
                typedef uint16_t queue_index_type;
                bool putMessage(AppMessage& msg, const queue_index_type& index);
                bool isValid(const session_id_type& session_id) const;
                void onMessageReceived(AppMessage& msg, uint64_t& pos, bool end_of_batch);
                bool addTask(WhisperTask* p_task);
                void initialAllTask();
                void deallocTransaction(const session_id_type& session_id);
            private:
                typedef WhisperSession session_type;
                map< WhisperSession::TaskTypeEnum, unique_ptr < WhisperTask > > _task_map;
                zhicloud::util::logger_type logger;
                session_id_type _session_count;
                std::atomic< session_id_type > _last_seed;
                session_id_type _min_session;
                session_id_type _max_session;
                uint16_t _queue_count;
                map< session_id_type, WhisperSession > _session_map;
                map< session_id_type, zhicloud::util::CopyableAtomic< bool > > _allocate_map;
                const static size_t queue_size = 1024;
                map< queue_index_type,  zhicloud::service::ActiveQueue < AppMessage, queue_size > > _queue_map;
                atomic< queue_index_type > _index_seed;

        };

    }
}


#endif // WHISPER_TASK_MANAGER_H

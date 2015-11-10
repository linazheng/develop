#ifndef BASE_MANAGER_HPP_INCLUDED
#define BASE_MANAGER_HPP_INCLUDED

#include <vector>
#include <list>
#include <map>
#include <memory>
#include <exception>
#include <thread>
#include <mutex>
#include <atomic>
#include <service/runable.hpp>
#include <service/active_queue.hpp>
#include <util/copyable_atomic.hpp>
#include <util/logging.h>
#include <transport/app_message.h>
#include <boost/bind.hpp>

using zhicloud::transport::AppMessage;
using namespace zhicloud::util;
using zhicloud::service::ActiveQueue;

namespace zhicloud{
    namespace transaction{

        template < class T >
        class BaseManager: public zhicloud::service::Runable
        {
        public:
            typedef typename T::session_type::session_id_type session_id_type;
            typedef typename T::session_type session_type;
            typedef typename T::task_id_type task_id_type;
            typedef T task_type;
            BaseManager(const session_id_type& session_count, const uint16_t& queue_count):
                _session_count(session_count), _last_seed(0),
                _min_session(1), _max_session(session_count + _min_session - 1),
                _queue_count(queue_count)
            {
                logger = getLogger("BaseManager");
                for(session_id_type seed = 0; seed < _session_count; seed++){
                    session_id_type session_id = seed + _min_session;
                    _allocate_map.emplace(session_id, atomic< bool > (false));
                    _session_map.emplace(session_id, session_type(session_id));
                }
                logger->info(boost::format("<TaskManager>%d transaction session created")
                             %_session_count);
                for(uint16_t i = 0; i < _queue_count; i++){
                    queue_index_type index = i + 1;
                    _queue_map.emplace(index, ActiveQueue< AppMessage, queue_size >() );
                }
                for(auto& item:_queue_map){
                    item.second.bindHandler(boost::bind(&BaseManager< T >::onMessageReceived, this, _1, _2, _3));
                }
                logger->info(boost::format("<TaskManager>%d work queue(s) ready")
                             %_queue_count);
            }
            virtual ~BaseManager(){
                _task_map.clear();
            }
            bool addTask(task_type* p_task){
                const task_id_type& task_id = p_task->getTaskID();
                if(_task_map.end() != _task_map.find(task_id)){
                    logger->warn(boost::format("<TaskManager>add task fail, task %d already exists")
                                 %(uint32_t)task_id);
                    return false;
                }
                _task_map[task_id] = std::unique_ptr< task_type > (p_task);
                logger->info(boost::format("<TaskManager>add task success, task id %d")
                             %(uint32_t)task_id);
                return true;
            }
            bool startTransaction(const task_id_type& task_id, AppMessage& msg, session_id_type& session_id){
                bool expect(false);
                session_id_type last_seed = _last_seed.load();
                for(session_id_type offset = 0; offset < _session_count; offset++){
                    session_id = (last_seed + offset)%_session_count + _min_session;
                    expect = false;
                    if(_allocate_map[session_id].compare_exchange_strong(expect, true)){
//                        logger->info(boost::format("<TaskManager>[%x]debug:session [%08X] => allocated")
//                                  %std::this_thread::get_id() %session_id);
                        //unallocate
                        if(!_session_map[session_id].occupy(task_id)){
                            //occupy fail
                            expect = true;
                            _allocate_map[session_id].compare_exchange_strong(expect, false);
//                            if(_allocate_map[session_id].compare_exchange_strong(expect, false)){
//                                logger->info(boost::format("<TaskManager>[%x]debug:session [%08X] => re deallocated")
//                                      %std::this_thread::get_id() %session_id);
//                            }
                            continue;
                        }
                        _last_seed.store((session_id)%_session_count);
                        _index_seed.fetch_add(1);
                        queue_index_type index = (_index_seed.load())%_queue_count + 1;
                        _session_map[session_id].attach_index(index);
                        msg.transaction = session_id;
                        if(!putMessage(msg, index)){
                            //deallcoate
                            deallocTransaction(session_id);
                            return false;
                        }
                        return true;
                    }
                }
                return false;
            }

            void terminateTransaction(const session_id_type& session_id){
                AppMessage msg(AppMessage::message_type::EVENT, EventEnum::terminate);
                msg.session = session_id;
                processMessage(session_id, msg);
            }

            bool processMessage(const session_id_type& session_id, AppMessage& msg){
                if(!isValid(session_id))
                    return false;
                if(!_allocate_map[session_id].load())
                    return false;
                queue_index_type index = _session_map[session_id].attach_index();
                msg.transaction = session_id;
                return putMessage(msg, index);
            }
            bool containsTransaction(const session_id_type& session_id){
                if(!isValid(session_id))
                    return false;
                return _allocate_map[session_id].load();
            }

        protected:
            virtual bool onStart() override{
                for(auto& item:_queue_map){
                    item.second.start();
                }
                logger->info("<TaskManager>service started");
                return true;
            }
            virtual void onStopping() override{
                for(auto& item:_queue_map){
                    item.second.stop();
                }
            }
            virtual void onWaitFinish() override{
            }
            virtual void onStopped() override{
            }
        private:
            typedef uint16_t queue_index_type;
            bool putMessage(AppMessage& msg, const queue_index_type& index){
                map< queue_index_type,  zhicloud::service::ActiveQueue < AppMessage, queue_size > >::iterator ir =  _queue_map.find(index);
                if(_queue_map.end() == ir)
                    return false;
                return ir->second.put(msg);
            }
            void deallocTransaction(const session_id_type& session_id){
                if(!isValid(session_id))
                    return;
                bool expect(true);
                if(_allocate_map[session_id].compare_exchange_strong(expect, false)){
//                    logger->info(boost::format("<TaskManager>[%x]debug:session [%08X] => deallocated")
//                                  %std::this_thread::get_id() %session_id);
                    _session_map[session_id].reset();
                    return;
                }
            }

            void onMessageReceived(AppMessage& msg, uint64_t& pos, bool end_of_batch){
                session_id_type session_id = msg.transaction;
                if(!_allocate_map[session_id].load())
                    return;

                session_type& session = _session_map[session_id];
                const task_id_type& task_id = session.getTaskID();
                if(task_id_type::invalid == task_id){
                    //session deallocated
                    return;
                }
                typename map< task_id_type, std::unique_ptr< task_type > >::iterator ir = _task_map.find(task_id);
                if(_task_map.end() == ir){
                    logger->error(boost::format("<TaskManager>invoke session fail, invalid task %d for session [%08X]")
                                  %(uint32_t)task_id %session_id);
                    return;
                }
                task_type& task = *ir->second;
                try{
                    if(!session.isInitialed()){
                        task.initialSession(msg, session);
                        task.invokeSession(session);
                    }
                    else{
                        task.processMessage(msg, session);
                    }
                    if(session.isFinished()){
                        task.releaseResource(session);
//                            logger->info(boost::format("<TaskManager>release finished session[%08X] by work thread[%x], last message %d, type %d")
//                                                %session_id %this_thread::get_id() %msg.id %(uint32_t)msg.type);
                        deallocTransaction(session_id);
                        return;
                    }
                }
                catch(std::exception& ex){
                    logger->error(boost::format("<TaskManager>process message exception in thread [%x], session[%08X], message %d, exception:%s")
                                  %this_thread::get_id() %session_id %msg.id %ex.what());
                    deallocTransaction(session_id);
                    return;
                }
                catch(...){
                    logger->error(boost::format("<TaskManager>process message unknown exception in thread [%x], session[%08X], message %d")
                                  %this_thread::get_id() %session_id %msg.id);
                    deallocTransaction(session_id);
                    return;
                }

            }

            bool isValid(const session_id_type& session_id){
                if((session_id < _min_session)||(session_id > _max_session))
                    return false;
                return true;
            }
        private:
            logger_type logger;
            session_id_type _session_count;
            atomic< session_id_type > _last_seed;
            session_id_type _min_session;
            session_id_type _max_session;
            uint16_t _queue_count;
            map< task_id_type, std::unique_ptr< task_type > > _task_map;
            map< session_id_type, session_type > _session_map;
            map< session_id_type, CopyableAtomic< bool > > _allocate_map;
            const static size_t queue_size = 1024;
            map< queue_index_type,  ActiveQueue < AppMessage, queue_size > > _queue_map;
            std::atomic< queue_index_type > _index_seed;
        };
    }
}

#endif // BASE_MANAGER_HPP_INCLUDED

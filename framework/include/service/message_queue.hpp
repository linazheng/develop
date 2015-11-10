#ifndef MESSAGE_QUEUE_HPP_INCLUDED
#define MESSAGE_QUEUE_HPP_INCLUDED

#include <memory>
#include <list>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <service/runable.hpp>
#include <service/event.hpp>
#include <thread>
#include <mutex>

using namespace std;

namespace zhicloud{
    namespace service{
        template < typename T >
        class MessageQueue:public Runable
        {
        private:
            typedef unique_lock<std::mutex> lock_type;
        public:
            typedef list< T > queue_type;
            typedef boost::signals2::signal< void (queue_type&) > event_type;
            typedef typename event_type::slot_type event_handler;
            MessageQueue(const uint32_t& max_batch = 100, const uint32_t& max_queue = 10000):
                max_batch(max_batch), max_queue(max_queue)
            {
            }
            virtual ~MessageQueue(){
            }
            void bindHandler(const event_handler& handler){
                onMessageReceived.connect(handler);
            }
            bool putMessage(const T& msg){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to tail
                message_queue.push_back(msg);
                message_available.set();
                return true;
            }
            bool putMessage(T&& msg){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to tail
                message_queue.push_back(std::move(msg));
                message_available.set();
                return true;
            }
            bool insertMessage(const T& msg){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to front
                message_queue.push_front(msg);
                message_available.set();
                return true;
            }
            bool insertMessage(T&& msg){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to front
                message_queue.push_front(std::move(msg));
                message_available.set();
                return true;
            }
            bool putMessage(const queue_type& msg_queue){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to tail
                for(const T& msg:msg_queue){
                    message_queue.push_back(msg);
                }
                message_available.set();
                return true;
            }
            bool putMessage(queue_type&& msg_queue){
                lock_type lock(mutex);
                if(max_queue <= message_queue.size())
                    return false;
                //copy to tail
                for(T& msg:msg_queue){
                    message_queue.push_back(std::move(msg));
                }
                message_available.set();
                return true;
            }
        protected:
            virtual bool onStart() override{
                work_thread = std::unique_ptr< thread >(new thread(&MessageQueue< T >::dispatchProcess,
                                                                                                this));
                return true;
            }
            virtual void onStopping() override{
                lock_type lock(mutex);
                message_available.set();
            }
            virtual void onWaitFinish() override
            {
                work_thread->join();
            }
            virtual void onStopped(){
                work_thread.reset();
            }
        private:
            void dispatchProcess(){
                queue_type notify_queue;
                uint32_t fetch_count;
                typename queue_type::size_type current_size;
                while(isRunning()){
                    {
                        message_available.wait();
                        if(!isRunning())
                        {
                            //invoke other thread
                            message_available.set();
                            break;
                        }
                        lock_type lock(mutex);
                        if(message_queue.empty())
                            continue;
                        notify_queue.clear();
                        current_size = message_queue.size();
                        fetch_count = min((uint32_t)current_size, max_batch);
                        if(fetch_count < (uint32_t)current_size){
                            //more msg left, invoke other thread
                            message_available.set();
                        }
                        for(uint32_t i = 0; i < fetch_count;i++){
                            notify_queue.push_back(std::move(message_queue.front()));
                            message_queue.pop_front();
                        }
                    }
                    onMessageReceived(notify_queue);
                }
            }

        private:
            uint32_t max_batch;
            uint32_t max_queue;
            event_type onMessageReceived;
            std::unique_ptr< thread > work_thread;
            std::mutex mutex;
            Event message_available;
            queue_type message_queue;
        };
    }

}

#endif // MESSAGE_QUEUE_HPP_INCLUDED

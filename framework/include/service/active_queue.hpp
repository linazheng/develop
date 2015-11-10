#ifndef FAST_QUEUE_H__
#define FAST_QUEUE_H__

#include <atomic>
#include <thread>
#include <array>
#include <exception>
#include <mutex>
#include <condition_variable>
#include <boost/signals2.hpp>
#include "runable.hpp"

//debug
//#include <boost/log/trivial.hpp>
//#include <boost/format.hpp>

namespace zhicloud{
    namespace service{

        template < typename T, size_t BufferSize >
        class ActiveQueue:public Runable
        {
        private:
            class StoppedException:public std::exception{};
            class PaddedUInt{
            private:
                volatile uint64_t value = 0;
                volatile uint64_t p1 = 1, p2 = 2, p3 = 3, p4 = 4, p5 =5 , p6 = 6, p7= 7;
            public:
                PaddedUInt(){}
                PaddedUInt(const uint64_t& t):value(t){
                }
                void set(const uint64_t& t){
                    value = t;
                }
                uint64_t get() const{
                    return value;
                }
                uint64_t preventOptimize(){
                    return p1 + p2 + p3 + p4 + p5 + p6 + p7;
                }
            };

            class PaddedAtomicUInt{
            private:
                std::atomic< uint64_t > value;
                volatile uint64_t p1 = 1, p2 = 2, p3 = 3, p4 = 4, p5 =5 , p6 = 6, p7= 7;
            public:
                PaddedAtomicUInt():value(0)
                {}
                PaddedAtomicUInt(const uint64_t& t):value(t){
                }
                void store(const uint64_t& t){
                    value.store(t);
                }
                uint64_t load() const{
                    return value.load();
                }
                bool compare_exchange_strong(uint64_t& expect, const uint64_t& v){
                    return value.compare_exchange_strong(expect, v);
                }
                uint64_t preventOptimize(){
                    return p1 + p2 + p3 + p4 + p5 + p6 + p7;
                }
            };

            typedef uint64_t position_type;
            typedef PaddedUInt barrier_type;
            typedef PaddedAtomicUInt seqence_type;
        public:
            typedef boost::signals2::signal< void (T&, uint64_t&, bool ) > event_type;
            typedef typename event_type::slot_type event_handler;
            enum class WaitStrategyEnum: uint16_t{
                Blocking = 0,
                Spin = 1,
                Yield = 2,
                Sleep = 3
            };

            ActiveQueue(const WaitStrategyEnum& strategy = WaitStrategyEnum::Blocking):ring_cursor(0), consume_cursor(0), gating_position(0),ring_mask(BufferSize - 1),
                wait_strategy(strategy), need_signal(false)
            {
                position_type left = BufferSize >> 1;
                ring_shift = 0;
                while( 0 != left){
                    ring_shift++;
                    left = left >> 1;
                }
                uint64_t initial_flag(0xFFFFFFFFFFFFFFFF);
                ring_flag.fill(initial_flag);
            }
            ~ActiveQueue(){
            }

            void bindHandler(const event_handler& handler){
                onEvent.connect(handler);
            }
            //copy to queue
            bool put(const T& t){
                try{
                    position_type pos = next();
                    setSlot(pos, t);
                    publishSlot(pos);
//                    BOOST_LOG_TRIVIAL(info) << boost::format("[%x]element copy to pos %d") %std::this_thread::get_id() %pos;
                    return true;
                }
                catch(StoppedException& ex){
                    return false;
                }
            }
            //move
            bool put(T&& t){
                try{
                    position_type pos = next();
                    setSlot(pos, std::move(t));
                    publishSlot(pos);
//                    BOOST_LOG_TRIVIAL(info) << boost::format("[%x]element moved to pos %d") %std::this_thread::get_id() %pos;
                    return true;
                }
                catch(StoppedException& ex){
                    return false;
                }
            }
            ActiveQueue(const ActiveQueue& other):ring_mask(BufferSize - 1)
            {
                copy(other);
            }
            ActiveQueue& operator=(const ActiveQueue& other){
                copy(other);
                return *this;
            }

        protected:
            virtual bool onStart(){
                dispatch_thread = std::thread(&ActiveQueue< T, BufferSize >::dispatchProcess, this);
//                BOOST_LOG_TRIVIAL(info) << boost::format("dispatch thread[%x]started") %dispatch_thread.get_id();
                return true;
            }
            virtual void onStopping(){
                signalWhenBlocking();
            }
            virtual void onWaitFinish(){
                dispatch_thread.join();
//                BOOST_LOG_TRIVIAL(info) << boost::format("dispatch thread[%x]stopped") %dispatch_thread.get_id();
            }
//            virtual void onStopped();
        private:
            position_type next(){
                return next(1);
            }
            position_type next(const size_t& quantity){
                if(0 == quantity){
                    throw std::logic_error("Invalid request quantity");
                }
                position_type current, next;
                while(true){
                    current = ring_cursor.load();
                    next = current + quantity;
                    position_type warp_pos(0);
                    if(next > BufferSize){
                        warp_pos = next - BufferSize;
                    }
                    position_type cached_gating = gating_position.get();
//                    BOOST_LOG_TRIVIAL(info) << "next:" << current << ", " << next << "," << warp_pos << "," << cached_gating;
                    if((warp_pos > cached_gating)||(cached_gating > current)){
                        position_type new_gating = std::min(consume_cursor.load(), current);
                        if(warp_pos > new_gating){
                            //need sleep&keep waiting
                            nap();
                            continue;
                        }
                        //update new gating
                        gating_position.set(new_gating);
                    }
                    else if(ring_cursor.compare_exchange_strong(current, next))
                    {
                        //set&forward
                        break;
                    }
                }
                return next;
            }
            //nap for a while
            void nap(){
                checkStatus();
                std::this_thread::yield();
            }

            position_type waitAvailableSlot(const position_type& expect){
                position_type available(0);
                switch(wait_strategy){
                case WaitStrategyEnum::Blocking:
                    {
                        if((available = ring_cursor.load()) < expect){
                            //need blocking
                            lock_type lock(wait_mutex);
                            do{
                                need_signal.store(true);
                                if((available = ring_cursor.load()) >= expect){
                                    break;
                                }
                                checkStatus();
                                wait_event.wait_for(lock, std::chrono::milliseconds(10));
                            }
                            while((available = ring_cursor.load()) < expect);
                        }
                        break;
                    }
                case WaitStrategyEnum::Spin:
                    {
                        while((available = ring_cursor.load()) < expect){
                            checkStatus();
                        }
                        break;
                    }
                case WaitStrategyEnum::Sleep:
                    {
                        const size_t intial_count(200);
                        size_t counter = intial_count;
                        while((available = ring_cursor.load()) < expect){
                            checkStatus();
                            if(counter > 100){
                                counter--;
                            }
                            else if(counter >0 ){
                                counter--;
                                std::this_thread::yield();
                            }
                            else{
                                std::this_thread::sleep_for(std::chrono::nanoseconds(1));
                            }
                        }
                        break;
                    }

                default:
                    //yield with initial spin
                    {
                        const size_t intial_count(100);
                        size_t counter = intial_count;
                        while((available = ring_cursor.load()) < expect){
                            checkStatus();
                            if(0 == counter){
                                std::this_thread::yield();
                            }
                            else{
                                counter--;
                            }
                        }
                        break;
                    }
                }//eof switch

                while(!isAvailable(expect)){
                    //make sure expcet available
                    checkStatus();
                }
                return available;
            }
            position_type waitPublishedSlot(const position_type& expect){
                checkStatus();
                position_type available = waitAvailableSlot(expect);
                if(available == expect){
                    return available;
                }
                return getHighestPublished(expect + 1, available);
            }
            position_type getHighestPublished(const position_type& lower, const position_type& available){
                for(uint64_t pos = lower; pos <= available;pos++){
                    if(!isAvailable(pos)){
                        return pos - 1;
                    }
                }
                //all published
                return available;
            }
            void setSlot(const position_type& pos, const T& t){
                //copy element
                ring_buffer[pos&ring_mask] = t;
            }
            void setSlot(const position_type& pos, T&& t){
                ring_buffer[pos&ring_mask] = std::move(t);
            }
            T& getSlot(const position_type& pos){
                return ring_buffer[pos&ring_mask];
            }
            void publishSlot(const position_type& pos){
                setAvailable(pos);
                signalWhenBlocking();
            }
            void setAvailable(const position_type& pos){
                position_type flag = pos >> ring_shift;
                ring_flag[pos&ring_mask] = flag;
            }
            bool isAvailable(const position_type& pos){
                position_type flag = pos >> ring_shift;
                return (flag == ring_flag[pos&ring_mask] );
            }
            void signalWhenBlocking(){
                if(WaitStrategyEnum::Blocking == wait_strategy){
                    //signal
                    bool true_flag(true);
                    if(need_signal.compare_exchange_strong(true_flag, false)){
                        lock_type lock(wait_mutex);
                        wait_event.notify_all();
                    }
                }
            }
            void dispatchProcess(){
                T event;
                position_type next_pos = consume_cursor.load() + 1;
                while(isRunning()){
                    try{
                        //single thread only
                        //todo:support multithread consumer
                        const position_type available_pos = waitPublishedSlot(next_pos);
                        while(next_pos <= available_pos){
                            //copy event
                            event = getSlot(next_pos);
                            onEvent(event, next_pos, next_pos == available_pos);
                            next_pos++;
                        }
                        //forward consumer
                        consume_cursor.store(available_pos);
                    }
                    catch(StoppedException& ex){
                        //stopped
//                        BOOST_LOG_TRIVIAL(info)  << "queue stopped";
                        break;
                    }
                    catch(std::exception& ex){
                        //todo:handle exception
                        consume_cursor.store(next_pos);
                        next_pos++;
                    }
                }
            }
            void checkStatus(){
                if(!isRunning()){
                    throw StoppedException();
                }
            }
            void copy(const ActiveQueue& other){
                ring_buffer = other.ring_buffer;
                ring_flag = other.ring_flag;
                ring_cursor.store(other.ring_cursor.load());
                consume_cursor.store(other.consume_cursor.load());
                gating_position.set(other.gating_position.get());
                ring_shift = other.ring_shift;
                wait_strategy = other.wait_strategy;
                need_signal.store(other.need_signal.load());
            }
        private:
            std::array< T, BufferSize > ring_buffer;
            std::array< volatile uint64_t, BufferSize > ring_flag;
            seqence_type ring_cursor;
            seqence_type consume_cursor;
            barrier_type gating_position;
            std::thread dispatch_thread;
            const position_type ring_mask;
            position_type ring_shift;
            WaitStrategyEnum wait_strategy;
            event_type onEvent;
            std::mutex wait_mutex;
            typedef std::unique_lock< std::mutex > lock_type;
            std::condition_variable wait_event;
            std::atomic< bool > need_signal;
        };
    }
}

#endif // FAST_QUEUE_H__

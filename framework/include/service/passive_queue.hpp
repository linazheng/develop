#ifndef PASSIVE_QUEUE_H__
#define PASSIVE_QUEUE_H__

#include <atomic>
#include <thread>
#include <array>
#include <exception>
#include <mutex>
#include <condition_variable>

namespace zhicloud{
    namespace service{

        template < typename T, size_t BufferSize >
        class PassiveQueue
        {
        private:
            class InvalidateException:public std::exception{};
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
            PassiveQueue():ring_cursor(0), consume_cursor(0), gating_position(0),
                ring_mask(BufferSize - 1), need_signal(false), invalidate_flag(false)
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
            ~PassiveQueue(){
            }
            //copy to queue
            void put(const T& t){
                try{
                    position_type pos = next();
                    setSlot(pos, t);
                    publishSlot(pos);
                }
                catch(InvalidateException& ex){
                    return;
                }

            }
            bool get(T& t){
                try{
                    //supprt multithread consumer
                    position_type current_pos, next_pos;
                    do{
                        current_pos = consume_cursor.load();
                        next_pos = current_pos + 1;
                        waitPublishedSlot(next_pos);
                        //cache event
                        t = getSlot(next_pos);
                        //forward cursor
                    }while(!consume_cursor.compare_exchange_strong(current_pos, next_pos));
                    //forward success
                    return true;
                }
                catch(InvalidateException){
                    return false;
                }
            };
            void invalidate(){
                invalidate_flag.store(true);
                signalWhenBlocking();
            }
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
                //signal
                bool true_flag(true);
                if(need_signal.compare_exchange_strong(true_flag, false)){
                    lock_type lock(wait_mutex);
                    wait_event.notify_all();
                }
            }
            void checkStatus(){
                if(invalidate_flag.load()){
                    throw InvalidateException();
                }
            }
        private:
            std::array< T, BufferSize > ring_buffer;
            std::array< volatile uint64_t, BufferSize > ring_flag;
            seqence_type ring_cursor;
            seqence_type consume_cursor;
            barrier_type gating_position;
            const position_type ring_mask;
            position_type ring_shift;
            std::mutex wait_mutex;
            typedef std::unique_lock< std::mutex > lock_type;
            std::condition_variable wait_event;
            std::atomic< bool > need_signal;
            std::atomic< bool > invalidate_flag;
        };
    }
}

#endif // FAST_QUEUE_H__

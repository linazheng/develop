#ifndef EVENT_HPP_INCLUDED
#define EVENT_HPP_INCLUDED

#include <atomic>
#include <thread>
#include <chrono>
#include <condition_variable>

using namespace std;

namespace zhicloud{
    namespace service{
        class Event{
            public:
                Event(bool is_set = false):value(is_set)
                {

                }
                ~Event(){
                }
                void set(){
                    bool expect(false);
                    std::unique_lock< std::mutex > lock(inner_mutex);
                    value.compare_exchange_strong(expect, true);
                    inner_contidion.notify_one();
                }
                void wait(){
                    bool expect(true);
                    std::unique_lock< std::mutex > lock(inner_mutex);
                    if(!value.load()){
                        //not set
                        inner_contidion.wait(lock);
                    }
                    //clear flag
                    value.compare_exchange_strong(expect, false);

                }
                template< class Rep, class Period >
                bool wait_for(const chrono::duration< Rep, Period >& timeout){
                    std::unique_lock< std::mutex > lock(inner_mutex);
                    bool expect(true);
                    if(!value.load()){
                        //not set
                        cv_status result =  inner_contidion.wait_for(lock, timeout);
                        if(cv_status::timeout == result){
                            //timeout
                            return false;
                        }
                    }
                    //clear flag
                    value.compare_exchange_strong(expect, false);
                    return true;
                }
                void clear(){
                    std::unique_lock< std::mutex > lock(inner_mutex);
                    bool expect(true);
                    value.compare_exchange_strong(expect, false);
                }

            private:
                Event(const Event& other);
                Event& operator=(const Event& other);
            private:
                std::atomic< bool > value;
                std::mutex inner_mutex;
                std::condition_variable inner_contidion;

        };
    }
}

#endif // EVENT_HPP_INCLUDED

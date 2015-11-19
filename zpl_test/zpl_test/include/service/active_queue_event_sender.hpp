#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <string>
#include <boost/log/trivial.hpp>
#include <boost/bind.hpp>
#include <boost/format.hpp>
#include <service/active_queue.hpp>

using namespace std;
using namespace std::chrono;

using namespace zhicloud::service;


class SampleEvent{
private:
    uint64_t int_value;
    string string_value;
public:
    SampleEvent():int_value(0){
    }

    void setInt(const uint64_t& t){
        int_value = t;
    }

    const uint64_t& getInt() const{
        return int_value;
    }

    void setString(const string& content){
        string_value = content;
    }

    const string& getString() const{
        return string_value;
    }

    SampleEvent(const SampleEvent& other){
        int_value = other.int_value;
        string_value = other.string_value;
    }

    SampleEvent& operator=(const SampleEvent& other){
        int_value = other.int_value;
        string_value = other.string_value;
        return *this;
    }

};

class ActiveQueueEventSender{
public:
    ActiveQueueEventSender(const size_t& count_per_sender, const size_t& sender = 1):
        put_thread_count(sender), put_count_per_thread(count_per_sender), received_count(0),
        expect_value(0), expect_pos(1), result(false),
        event_queue(ActiveQueue< SampleEvent, buffer_size >::WaitStrategyEnum::Blocking)
    {
        total_count = put_thread_count * put_count_per_thread;
        event_queue.bindHandler(boost::bind(&ActiveQueueEventSender::onSingleEventSender, this, _1, _2, _3));
    }
    ~ActiveQueueEventSender(){
    }
    bool test(){
        event_queue.start();
        vector< thread > put_threads;
        for(size_t i =0; i < put_thread_count;i++){
            put_threads.push_back(thread(&ActiveQueueEventSender::sendProcess, this));
        }
        {
            lock_type lock(event_mutex);
            finish_event.wait(lock);
        }
        for(size_t i =0; i < put_thread_count;i++){
            put_threads[i].join();
        }
        event_queue.stop();
        return result;
    }
private:
    void sendProcess(){
        chrono::time_point< chrono::high_resolution_clock > begin_time = chrono::high_resolution_clock::now();
        SampleEvent event;
        event.setString("zhicloud");
        for(uint64_t value = 0;value < put_count_per_thread; value++){
            event.setInt(value);
            event_queue.put(event);
        }
        uint64_t elapsed = duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - begin_time).count();
        uint64_t speed = uint64_t(double(put_count_per_thread*1000000)/elapsed);
        BOOST_LOG_TRIVIAL(info)  << boost::format("%d event put in %.04f millisecond(s), speed %d event/s") %total_count % (elapsed/1000 ) %speed;
    }
    void onSingleEventSender(SampleEvent& t, uint64_t& pos, bool end_of_batch){
        if(0 == received_count){
            fetch_begin = chrono::high_resolution_clock::now();
        }
        if(0 != t.getString().compare("zhicloud")){
            BOOST_LOG_TRIVIAL(info)  << "string value corrupt in pos " << pos;
            lock_type lock(event_mutex);
            finish_event.notify_all();
            return;
        }
        if(expect_value != t.getInt()){
            BOOST_LOG_TRIVIAL(info)  << "unexpect value " << t.getInt() << " received, expect :" << expect_value ;
            lock_type lock(event_mutex);
            finish_event.notify_all();
            return;
        }
        else if (expect_pos != pos){
            BOOST_LOG_TRIVIAL(info)  << "unexpect pos " << pos << " received, expect :" << expect_pos ;
            lock_type lock(event_mutex);
            finish_event.notify_all();
            return;
        }
        else{
            expect_pos++;
            expect_value++;
            received_count++;
            if(received_count >= total_count){
                uint64_t elapsed = duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - fetch_begin).count();
                uint64_t speed = uint64_t(double(received_count*1000000)/elapsed);
                BOOST_LOG_TRIVIAL(info)  << boost::format("%d event fetched in %.04f millisecond(s), speed %d event/s") %received_count % (elapsed/1000 ) %speed;
                result = true;
                lock_type lock(event_mutex);
                finish_event.notify_all();
                return;
            }
        }
    }

private:
    const static size_t buffer_size = 1024;
    size_t put_thread_count;
    size_t put_count_per_thread;
    size_t received_count;
    size_t total_count;
    uint64_t expect_value;
    uint64_t expect_pos;
    bool result;
    std::condition_variable finish_event;
    std::mutex event_mutex;
    typedef std::unique_lock< std::mutex > lock_type;
    ActiveQueue< SampleEvent, buffer_size > event_queue;
    chrono::time_point< chrono::high_resolution_clock > fetch_begin;
};

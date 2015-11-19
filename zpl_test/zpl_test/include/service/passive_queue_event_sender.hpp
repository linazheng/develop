#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <string>
#include <boost/log/trivial.hpp>
#include <boost/bind.hpp>
#include <boost/format.hpp>
#include <service/passive_queue.hpp>

using namespace std;
using namespace std::chrono;

using namespace zhicloud::service;

class PassiveQueueEventSender{
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
public:
    PassiveQueueEventSender(const size_t& count_per_producer, const size_t& producer = 1, const size_t& consumer = 1):
        producer_count(producer), event_per_producer(count_per_producer), consumer_count(consumer),
        total_count(0), recevied_count(0), produce_summary(0), consume_summary(0)
    {
        total_count = event_per_producer * producer_count;
    }
    ~PassiveQueueEventSender(){
    }
    bool test(){
//        BOOST_LOG_TRIVIAL(info)  << "active queue started" ;
        vector< thread > producer_threads;
        for(size_t i =0; i < producer_count;i++){
            producer_threads.push_back(thread(&PassiveQueueEventSender::putProcess, this));
        }
        //consumer thread
        vector< thread > consumer_threads;
        for(size_t i =0; i < consumer_count;i++){
            consumer_threads.push_back(thread(&PassiveQueueEventSender::getProcess, this));
        }
        {
            lock_type lock(event_mutex);
            finish_event.wait(lock);
        }
        event_queue.invalidate();

        for(size_t i =0; i < producer_count;i++){
            producer_threads[i].join();
        }
        for(size_t i =0; i < consumer_count;i++){
            consumer_threads[i].join();
        }
        if(total_count != recevied_count.load()){
            BOOST_LOG_TRIVIAL(error)  << boost::format("test fail, only %d / %d event received") %recevied_count.load() % total_count;
            return false;
        }
        if(consume_summary.load() != produce_summary.load()){
            BOOST_LOG_TRIVIAL(error)  << boost::format("test fail, only %d / %d summary received") %consume_summary.load()  % produce_summary.load();
            return false;
        }
        return true;
    }
private:
    void putProcess(){
        chrono::time_point< chrono::high_resolution_clock > begin_time = chrono::high_resolution_clock::now();
        SampleEvent event;
        event.setString("zhicloud");
        for(uint64_t value = 0;value < event_per_producer; value++){
            event.setInt(value);
            event_queue.put(event);
            produce_summary.fetch_add(value);
        }
        uint64_t elapsed = duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - begin_time).count();
        uint64_t speed = uint64_t(double(event_per_producer*1000000)/elapsed);
        BOOST_LOG_TRIVIAL(info)  << boost::format("%d event put in %.04f millisecond(s), speed %d event/s") %event_per_producer % (elapsed/1000 ) %speed;
    }
    void getProcess(){
        SampleEvent event;
        chrono::time_point< chrono::high_resolution_clock > begin_time = chrono::high_resolution_clock::now();
        uint64_t local_count(0);
        do{
            if(!event_queue.get(event)){
                //invalidate
                break;
            }
            if(0 != event.getString().compare("zhicloud")){
                BOOST_LOG_TRIVIAL(info)  << "string value corrupted";
                lock_type lock(event_mutex);
                finish_event.notify_all();
                return;
            }
            local_count++;
            recevied_count.fetch_add(1);
            consume_summary.fetch_add(event.getInt());
        }while(recevied_count.load() < total_count);

        uint64_t elapsed = duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - begin_time).count();
        uint64_t speed = uint64_t(double(local_count*1000000)/elapsed);
        BOOST_LOG_TRIVIAL(info)  << boost::format("get %d event in %.04f millisecond(s), speed %d event/s") %local_count % (elapsed/1000 ) %speed;
        lock_type lock(event_mutex);
        finish_event.notify_all();
    }
private:
    const static size_t buffer_size = 1024;
    size_t producer_count;
    size_t event_per_producer;
    size_t consumer_count;
    size_t total_count;
    atomic< uint64_t > recevied_count;
    atomic< uint64_t > produce_summary;
    atomic< uint64_t > consume_summary;
    std::condition_variable finish_event;
    std::mutex event_mutex;
    typedef std::unique_lock< std::mutex > lock_type;
    PassiveQueue< SampleEvent, buffer_size > event_queue;
    chrono::time_point< chrono::high_resolution_clock > fetch_begin;
};

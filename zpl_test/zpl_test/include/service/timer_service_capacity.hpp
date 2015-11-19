#ifndef TIMER_SERVICE_CAPACITY_HPP_INCLUDED
#define TIMER_SERVICE_CAPACITY_HPP_INCLUDED


#include <chrono>
#include <map>
#include <mutex>
#include <list>
#include <condition_variable>
#include <transport/app_message.h>
#include <service/timer_service.h>
#include <boost/bind.hpp>

using namespace std;
using zhicloud::service::TimerService;
using zhicloud::transport::AppMessage;

class TimerServiceCapacity{
        typedef int16_t timer_id_type;
    public:
        TimerServiceCapacity():_capacity(64), _max_capacity(_capacity * 3), _timeout_per_batch(2),
            _timer_service(std::chrono::milliseconds(1), _capacity) ,_result(false)
        {
        }
        ~TimerServiceCapacity(){
        }
        bool test(){
            try{
                list< uint32_t > timeout_list = {1, 2, 3, 4, 5};
                size_t batch_size(10);

                _timer_service.bindHandler(boost::bind(&TimerServiceCapacity::onTimeoutEvent, this, _1));
                _timer_service.start();
                {
                    uint32_t session_id(1);
                    lock_type lock(_mutex);
                    for(const uint32_t& timeout:timeout_list){
                        for(size_t i = 0; i< batch_size;i++){
                            timer_id_type timer_id = _timer_service.setTimer(std::chrono::milliseconds(timeout), session_id);
                            _timepoint_map.emplace(timer_id, chrono::high_resolution_clock::now());
                            _timeout_map.emplace(timer_id, timeout);
                        }
                    }
                    BOOST_LOG_TRIVIAL(info) << boost::format("%d timer setted") %_timeout_map.size();
                }
                {
                    timeout_list.sort();
                    size_t batch_count(0);
                    if(0 == _max_capacity%batch_size){
                        batch_count = _max_capacity / batch_size;
                    }
                    else{
                        batch_count = (_max_capacity - _max_capacity%batch_size)/batch_size + 1;
                    }

                    size_t wait_time = (batch_count + 1) * _timeout_per_batch;
                    BOOST_LOG_TRIVIAL(info) << boost::format("max capacity %d, batch size %d, timeout %d, wait time %d")
                                                                    %_max_capacity %batch_size %_timeout_per_batch %wait_time;

                    lock_type lock(_mutex);
                    _finish_event.wait_for(lock, chrono::milliseconds(wait_time * 1000 + 500));
                    _timer_service.stop();
                }
                return _result;
            }
            catch(exception& ex){
                BOOST_LOG_TRIVIAL(info) << boost::format("exception when test, message:%s") %ex.what();
                _timer_service.stop();
                return false;
            }

        }
    private:
        void onTimeoutEvent(list < AppMessage >& event_list){
            for(const AppMessage& msg:event_list){
                BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]timer %d invoked") %msg.session %msg.sequence;
                timer_id_type timer_id = msg.sequence;
                lock_type lock(_mutex);
                map< timer_id_type, chrono::time_point< chrono::high_resolution_clock > >::iterator timepoint_ir = _timepoint_map.find(timer_id);
                if(_timepoint_map.end() == timepoint_ir){
                    BOOST_LOG_TRIVIAL(error) << boost::format("invalid timer %d") %timer_id;
                    return;
                }
                uint32_t elapsed = chrono::duration_cast< chrono::seconds >( chrono::high_resolution_clock::now() - timepoint_ir->second).count();
                map< timer_id_type, uint32_t >::iterator timeout_ir = _timeout_map.find(timer_id);
                if(_timeout_map.end() == timeout_ir){
                    BOOST_LOG_TRIVIAL(error) << boost::format("can't get timeout value for timer %d") %timer_id;
                    return;
                }
                if(timeout_ir->second != elapsed){
                    BOOST_LOG_TRIVIAL(error) << boost::format("timeout invoked in unexpect time, elapsed %d, expect %d") %elapsed %timeout_ir->second;
                    return;
                }
                if(timer_id >= _max_capacity){
                    BOOST_LOG_TRIVIAL(error) << boost::format("max timer %d invoked") %timer_id;
                    _result = true;
                    _finish_event.notify_all();
                    return;
                }
                _timeout_map.erase(timeout_ir);
                _timepoint_map.erase(timepoint_ir);
                //create new timer
                timer_id_type new_timer_id = _timer_service.setTimer(std::chrono::milliseconds(_timeout_per_batch), 1);
                _timepoint_map.emplace(new_timer_id, chrono::high_resolution_clock::now());
                _timeout_map.emplace(new_timer_id, _timeout_per_batch);
            }
        }
    private:
        map< timer_id_type, chrono::time_point< chrono::high_resolution_clock > > _timepoint_map;
        map< timer_id_type, uint32_t > _timeout_map;
        size_t _capacity;
        size_t _max_capacity;
        size_t _timeout_per_batch;
        TimerService _timer_service;
        mutex _mutex;
        bool _result;
        condition_variable _finish_event;
        typedef unique_lock< mutex > lock_type;

};


#endif // TIMER_SERVICE_CAPACITY_HPP_INCLUDED

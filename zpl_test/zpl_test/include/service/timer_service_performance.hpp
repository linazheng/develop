#ifndef TIMER_SERVICE_PERFORMANCE_HPP_INCLUDED
#define TIMER_SERVICE_PERFORMANCE_HPP_INCLUDED

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

class TimerServicePerformance{
        typedef int16_t timer_id_type;
    public:
        TimerServicePerformance():_result(false)
        {
        }
        ~TimerServicePerformance(){
        }
        bool test(){
            list< uint32_t > timeout_list = {2, 5};
            _timer_service.bindHandler(boost::bind(&TimerServicePerformance::onTimeoutEvent, this, _1));
            _timer_service.start();
            {
                uint32_t session_id(0);
                size_t count_per_batch(500);
                lock_type lock(_mutex);
                chrono::time_point< chrono::high_resolution_clock > begin_time = chrono::high_resolution_clock::now();
                for(const uint32_t& timeout:timeout_list){
                    session_id++;
                    for(size_t i = 0; i< count_per_batch; i++){
                        timer_id_type timer_id = _timer_service.setTimer(std::chrono::milliseconds(timeout), session_id);
                        _timer_map.emplace(timer_id, chrono::high_resolution_clock::now() );
                        _timeout_map.emplace(timer_id, timeout);
                    }
                }
                uint64_t elapsed = chrono::duration_cast< chrono::microseconds >( chrono::high_resolution_clock::now() - begin_time).count();
                size_t total_count = count_per_batch * timeout_list.size();
                if(0 == elapsed){
                    BOOST_LOG_TRIVIAL(info) << boost::format("%d timer setted in 0 macrosecond(s)")
                                                                        %total_count ;
                }
                else{
                    BOOST_LOG_TRIVIAL(info) << boost::format("%d timer setted in %.3f millisecond(s), speed %d / s")
                                                                        %total_count %((double)elapsed/1000) %(total_count*1000000/elapsed);
                }
            }
            timeout_list.sort();
            uint32_t max_timeout = timeout_list.back() + 2;
            {
                lock_type lock(_mutex);
                _finish_event.wait_for(lock, chrono::seconds(max_timeout));
            }
            _timer_service.stop();

            if(_timeout_map.empty()){
                _result = true;
            }
            else{
                BOOST_LOG_TRIVIAL(info) << boost::format("%d timer not properly invoked")
                                                                        %_timeout_map.size();
            }
            return _result;
        }
    private:
        void onTimeoutEvent(list < AppMessage >& event_list){
            for(const AppMessage& msg:event_list){
//                BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]timer %d invoked") %msg.session %msg.sequence;
                timer_id_type timer_id = msg.sequence;
                lock_type lock(_mutex);
                map< timer_id_type, chrono::time_point< chrono::high_resolution_clock > >::const_iterator timepoint_ir = _timer_map.find(timer_id);
                if(_timer_map.end() == timepoint_ir){
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
                else{
                    _timeout_map.erase(timeout_ir);
                    if(_timeout_map.empty())
                        _finish_event.notify_all();
                }
            }
        }
    private:
        map< timer_id_type, chrono::time_point< chrono::high_resolution_clock > > _timer_map;
        map< timer_id_type, uint32_t > _timeout_map;
        TimerService _timer_service;
        mutex _mutex;
        bool _result;
        condition_variable _finish_event;
        typedef unique_lock< mutex > lock_type;

};

#endif // TIMER_SERVICE_PERFORMANCE_HPP_INCLUDED

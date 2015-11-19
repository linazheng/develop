#ifndef TIMER_SERVICE_LOOP_TIMER_HPP_INCLUDED
#define TIMER_SERVICE_LOOP_TIMER_HPP_INCLUDED


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

class TimerServiceLoopTimer{
        typedef int16_t timer_id_type;
    public:
        TimerServiceLoopTimer():_result(false)
        {
        }
        ~TimerServiceLoopTimer(){
        }
        bool test(){
            try{
                vector< uint32_t > timeout_list = {1, 2, 3, 4, 5};

                //
    //            list< timer_id_type > id_list =  {1, 2, 3, 4, 5, 6, 7, 8};
                _timer_service.bindHandler(boost::bind(&TimerServiceLoopTimer::onTimeoutEvent, this, _1));
                _timer_service.start();
                {
                    uint32_t session_id(0);
                    lock_type lock(_mutex);
                    for(const uint32_t& interval:timeout_list){
                        session_id++;
                        timer_id_type timer_id = _timer_service.setLoopTimer(std::chrono::milliseconds(interval), session_id);
                        _timepoint_map.emplace(timer_id, chrono::high_resolution_clock::now() );
                        _timeout_map.emplace(timer_id, interval);
                        _counter_map.emplace(timer_id, 0);
                        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]timer %d set, interval %d second(s)") % session_id %timer_id %interval;
                    }
                }
                {
                    size_t wait_time(24);
                    //3.5s
                    this_thread::sleep_for(chrono::milliseconds(wait_time * 1000 + 500));

                    lock_type lock(_mutex);
                    for(auto& item:_counter_map){
                        const timer_id_type& timer_id = item.first;
                        if(!_timer_service.clearTimer(timer_id)){
                            throw logic_error((boost::format("can't clear loop timer %d")%timer_id).str());
                        }
                        BOOST_LOG_TRIVIAL(info) << boost::format("timer %d cleared") %timer_id;
                    }
                    _timer_service.stop();

                    for(auto& item:_counter_map){
                        const timer_id_type& timer_id = item.first;
                        const uint32_t& counter = item.second;
                        const uint32_t& interval = _timeout_map[timer_id];
                        uint32_t expect = (wait_time - wait_time%interval)/ interval;
                        if(expect != counter){
                            throw logic_error((boost::format("expect %d invoke for timer %d, but %d invoked")%expect %counter %timer_id).str());
                        }
                        BOOST_LOG_TRIVIAL(info) << boost::format("%d invoke counted for timer %d ")%counter %timer_id;
                    }
                }
                return true;

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
                map< timer_id_type, uint32_t >::iterator count_ir = _counter_map.find(timer_id);
                if(_counter_map.end() == count_ir){
                    BOOST_LOG_TRIVIAL(error) << boost::format("can't get counter for timer %d") %timer_id;
                    return;
                }
                count_ir->second++;
                timepoint_ir->second = chrono::high_resolution_clock::now();
            }
        }
    private:
        map< timer_id_type, chrono::time_point< chrono::high_resolution_clock > > _timepoint_map;
        map< timer_id_type, uint32_t > _timeout_map;
        map< timer_id_type, uint32_t > _counter_map;
        TimerService _timer_service;
        mutex _mutex;
        bool _result;
        condition_variable _finish_event;
        typedef unique_lock< mutex > lock_type;

};


#endif // TIMER_SERVICE_LOOP_TIMER_HPP_INCLUDED

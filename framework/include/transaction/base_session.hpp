#ifndef BASE_SESSION_H
#define BASE_SESSION_H

#include <string>
#include <list>
#include <mutex>
#include <transport/app_message.h>
#include <service/timer_service.h>

using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transaction{
        template < typename T >
        class BaseSession
        {
            protected:
                typedef std::lock_guard< std::mutex > lock_type;

            public:
                typedef uint32_t session_id_type;
                typedef uint32_t state_type;
                typedef T task_id_type;
                typedef zhicloud::service::TimerService::timer_id_type timer_id_type;

                BaseSession(const session_id_type& id):session_id(id){
                    reset();
                }
                BaseSession():BaseSession(0){
                }
                virtual ~BaseSession(){
                }
                void reset(){
                    lock_type lock(mutex);
                    task_id = T::invalid;
                    initialed = false;
                    current_state = (state_type)StateEnum::initial;
                    request_module.clear();
                    request_session = 0;
                    timer_id = zhicloud::service::TimerService::getInvalidTimer();
                    state_specified = false;
                    _loop_timer = false;
                    _allocated = false;
                    _attach_index = 0;
                    onReset();
                }
                bool occupy(const T& task){
                    lock_type lock(mutex);
                    if(_allocated)
                        return false;
                    task_id = task;
                    _allocated = true;
                    return true;
                }
                bool isInitialed(){
                    return initialed;
                }
                void initial(const AppMessage& msg){
                    initial_message = msg;
                    current_state = (state_type)StateEnum::initial;
                    request_module = msg.sender;
                    request_session = msg.session;
                    initialed = true;
                }
                constexpr static state_type getInitialState(){
                	return (state_type)StateEnum::initial;
                }
                constexpr static state_type getFinishState(){
                    return (state_type)StateEnum::finish;
                }
                bool isFinished() const{
                    return ((state_type)StateEnum::finish == current_state);
                }
                void finish(){
                    current_state = (state_type)StateEnum::finish;
                }
                void setState(const state_type& next_state){
                    if(current_state != (state_type)StateEnum::initial)
                    {
                        state_specified = true;
                    }
                    current_state = next_state;
                }

                AppMessage& getInitialMessage(){
                    return initial_message;
                }

                state_type getCurrentState() const{
                    return current_state;
                }
                void next(const state_type& state){
                    if((state_type)StateEnum::finish != current_state){
                        if(state_specified)
                            state_specified = false;
                        else
                            current_state = state;
                    }
                }

                void setTimerID(const timer_id_type& id, const bool& loop = false){
                    timer_id = id;
                    _loop_timer = loop;
                }
                const timer_id_type& getTimerID() const{
                    return timer_id;
                }
                bool isTimerSetted() const{
                    return (timer_id != zhicloud::service::TimerService::getInvalidTimer());
                }

                const bool& isLoopTimer() const{
                    return _loop_timer;
                }
                void resetTimer(){
                    _loop_timer = false;
                    timer_id = zhicloud::service::TimerService::getInvalidTimer();
                }

                const task_id_type& getTaskID() const{
                    return task_id;
                }
                const session_id_type& getSessionID() const{
                    return session_id;
                }
                const string& getRequestModule() const{
                    return request_module;
                }
                const session_id_type& getRequestSession() const{
                    return request_session;
                }

                const uint16_t& attach_index() const{
                    return _attach_index;
                }

                void attach_index(const uint16_t& value){
                    _attach_index = value;
                }

                BaseSession(BaseSession&& other){
                    move_contruct(std::move(other));
                }
                BaseSession& operator=(BaseSession&& other){
                    move_contruct(std::move(other));
                    return *this;
                }
            protected:
                virtual void onReset(){
                    //reset member here
                }
            private:
                void move_contruct(BaseSession&& other){
                    session_id = std::move(other.session_id);
                    task_id = std::move(other.task_id);
                    initialed = std::move(other.initialed);
                    current_state = std::move(other.current_state);
                    initial_message = std::move(other.initial_message);
                    request_module = std::move(other.request_module);
                    request_session = std::move(other.request_session);
                    timer_id = std::move(other.timer_id);
                    state_specified = std::move(other.state_specified);
                    _loop_timer = std::move(other._loop_timer);
                    _allocated = std::move(other._allocated);
                    _attach_index = std::move(other._attach_index);
                }
            protected:
                mutable std::mutex mutex;

            private:
                enum class StateEnum:state_type{
                        initial = 0,
                        finish = 0xFFFF,
                };
                session_id_type session_id;
                T task_id;
                bool initialed;
                state_type current_state;
                AppMessage initial_message;
                string request_module;
                session_id_type request_session;
                timer_id_type timer_id;
                bool state_specified;
                bool _loop_timer;
                bool _allocated;
                uint16_t _attach_index;


        };
    }
}



#endif // BASE_SESSION_H

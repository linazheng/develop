#ifndef TIMERSERVICE_H
#define TIMERSERVICE_H

#include <vector>
#include <atomic>
#include <chrono>
#include <mutex>
#include <transport/app_message.h>
#include <service/timed_invoker.h>
#include <util/copyable_atomic.hpp>

namespace zhicloud{
    namespace service{
        using zhicloud::transport::AppMessage;

        class TimerService
        {
            public:
                typedef uint32_t timer_id_type;
                typedef std::chrono::milliseconds timeout_type;
                typedef uint32_t session_id_type;
                typedef list< AppMessage > event_list_type;
                typedef boost::signals2::signal< void (event_list_type&) > event_type;
                typedef event_type::slot_type event_handler;

                TimerService(const timeout_type& interval_in_milliseconds = timeout_type(1000), const size_t& max_timer = 1024);
                virtual ~TimerService();
                void bindHandler(const event_handler& handler);
                bool start();
                void stop();
                timer_id_type setTimer(const timeout_type& milliseconds, const session_id_type& session_id);
                timer_id_type setLoopTimer(const timeout_type& interval_milliseconds, const session_id_type& session_id);
                timer_id_type setTimedEvent(const AppMessage& event, const timeout_type& milliseconds);
                timer_id_type setLoopTimedEvent(const AppMessage& event, const timeout_type& interval_milliseconds);
                bool clearTimer(const timer_id_type& timer_id);

                constexpr static timer_id_type getInvalidTimer(){
                    return 0;
                }

            private:
                void onCheckTimeout();

            private:
                class TimerCounter{
                public:
                    TimerCounter();
                    ~TimerCounter();
                    TimerCounter(TimerCounter&& other);
                    void reset();
                    bool allocate(const timer_id_type& timer_id, const session_id_type& session_id, const timeout_type& milliseconds, const bool& loop = false);
                    bool allocate(const timer_id_type& timer_id, const AppMessage& msg, const timeout_type& milliseconds, const bool& loop = false);
                    const timer_id_type& timer_id() const;
                    const std::chrono::time_point< std::chrono::high_resolution_clock >& timepoint() const;
                    const bool& event_specified() const;
                    const bool& is_loop() const;
                    const session_id_type& receive_session() const;
                    const AppMessage& event() const;
                    void next();
                private:
                    TimerCounter& operator=(TimerCounter&& other);

                private:
                    timer_id_type _timer_id;
                    session_id_type _receive_session;
                    timeout_type _timeout;
                    std::chrono::time_point< std::chrono::high_resolution_clock > _timepoint;
                    bool _is_loop;
                    bool _event_specified;
                    bool _allocated;
                    AppMessage _event;
                    mutable std::mutex _mutex;
                    typedef std::lock_guard< std::mutex > lock_type;
                };

                TimedInvoker _invoker;
                event_type onTimeoutInvoked;
                const static timer_id_type _min_timer_id;
                size_t _max_timer;
                std::vector< zhicloud::util::CopyableAtomic< bool > > _allocated;
                std::vector< TimerCounter > _timer_slot;
                std::atomic< timer_id_type > _id_seed;

        };
    }
}



#endif // TIMERSERVICE_H

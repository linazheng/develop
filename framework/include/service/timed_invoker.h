#ifndef TIMEDINVOKER_H
#define TIMEDINVOKER_H

#include <service/runable.hpp>
#include <boost/signals2.hpp>
#include <service/event.hpp>
#include <thread>
#include <chrono>

namespace zhicloud{
    namespace service{
        class TimedInvoker: public Runable
        {
            public:
                typedef boost::signals2::signal< void () > event_type;
                typedef event_type::slot_type event_handler;
                TimedInvoker(const std::chrono::milliseconds& interval_in_milli, const unsigned int& limit = 0);
                virtual ~TimedInvoker();
                void bindHandler(const event_handler& handler);
            protected:
                virtual bool onStart();
                virtual void onStopping();
                virtual void onWaitFinish();
                virtual void onStopped();
            private:
                void invokeProcess();
                void notifyProcess();
                event_type onTimeout;
            private:
                typedef std::chrono::milliseconds duration_type;
                duration_type interval;
                unsigned int limit;
                std::thread notify_thread;
                std::thread invoke_thread;
                Event timeout_event;
        };

    }
}



#endif // TIMEDINVOKER_H

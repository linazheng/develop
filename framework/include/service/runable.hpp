#ifndef RUNABLESERVICE_H
#define RUNABLESERVICE_H

#include <mutex>
#include <atomic>

namespace zhicloud{
    namespace service{
        class Runable
        {
            private:
                enum class ServiceStatus:uint16_t{
                    stopped = 0,
                    running = 1,
                    stopping = 2
                };
            public:
                Runable():status(ServiceStatus::stopped){}
                virtual ~Runable(){
                    stop();
                }
                bool start(){
                    lock_type lock(mutex);
                    ServiceStatus expect(ServiceStatus::stopped);
                    if(!status.compare_exchange_strong(expect, ServiceStatus::running)){
                        //not stopped
                        return false;
                    }
                    if(!onStart())
                    {
                        status.store(ServiceStatus::stopped);
                        return false;
                    }
                    return true;
                }
                void stop(){
                   {
                        lock_type lock(mutex);
                        if(ServiceStatus::stopped == status.load())
                            return;
                        ServiceStatus expect(ServiceStatus::running);
                        if(status.compare_exchange_strong(expect, ServiceStatus::stopping))
                        {
                            onStopping();
                        }
                    }
                    onWaitFinish();
                    {
                        lock_type lock(mutex);
                        status.store(ServiceStatus::stopped);
                    }
                    onStopped();
                }
                bool isRunning() const
                {
                    return (ServiceStatus::running == status.load());
                }
            protected:
                virtual bool onStart(){
                    return true;
                }
                virtual void onStopping(){}
                virtual void onWaitFinish(){}
                virtual void onStopped(){}
            private:
                volatile std::atomic<ServiceStatus> status;
                mutable std::recursive_mutex mutex;
                typedef std::lock_guard< std::recursive_mutex > lock_type;
        };
    }
}


#endif // RUNABLESERVICE_H


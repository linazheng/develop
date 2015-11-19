#ifndef SERVICE_UNIFY_TEST_H
#define SERVICE_UNIFY_TEST_H

//#include <service/event_test.h>
//#include <service/message_queue_test.h>
//#include <service/timed_invoker_test.h>
//#include <service/timer_service_test.h>


class ServiceUnifyTest{

    public:
        ServiceUnifyTest();
		~ServiceUnifyTest();
        bool test();
    private:
        bool testActiveQueue();
        bool testPassiveQueue();
};

#endif // SERVICE_UNIFY_TEST_H

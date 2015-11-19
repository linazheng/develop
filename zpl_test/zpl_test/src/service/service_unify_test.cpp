#include <iostream>
#include <exception>
#include <functional>
#include <boost/log/trivial.hpp>
#include <unistd.h>
#include "service/service_unify_test.h"
#include <service/active_queue.hpp>
#include <service/passive_queue.hpp>

#include "active_queue_test.h"
#include "passive_queue_test.h"

#include "event_test.h"
#include "message_queue_test.h"
#include "timed_invoker_test.h"
#include "timer_service_test.h"
#include "node_service_test.h"


using namespace std;
using namespace zhicloud::service;

ServiceUnifyTest::ServiceUnifyTest()
{

}
ServiceUnifyTest::~ServiceUnifyTest()
{

}

bool ServiceUnifyTest::test() {
    try{
        string section_name("service");
        BOOST_LOG_TRIVIAL(info) << "begin test section " << section_name << "...";
        bool test_node_service(false);
        bool test_active_queue(false);
        bool test_passive_queue(false);
        bool test_message_queue(false);
        bool test_timed_invoker(false);
        bool test_timer_service(true);
        bool test_event(false);

		if(test_node_service){
		    NodeServiceTest test;
			if (!test.test())
			{
                throw std::logic_error("node service test fail");
			}
            BOOST_LOG_TRIVIAL(info) << "node service test success";
		}
        if(test_active_queue){
            ActiveQueueTest test;
            if(!test.test()){
                throw std::logic_error("active queue test fail");
            }
            BOOST_LOG_TRIVIAL(info) << "active queue test success";
        }
        if(test_passive_queue){
            PassiveQueueTest test;
            if(!test.test()){
                throw std::logic_error("passive queue test fail");
            }
            BOOST_LOG_TRIVIAL(info) << "passive queue test success";
        }
		if(test_event){
			EventTest eventtest(5);
			if(!eventtest.test())
			{
                throw std::logic_error("EventTest test fail");
			}
            BOOST_LOG_TRIVIAL(info) << "EventTest test success";
		}
		if(test_message_queue){
			MessageQueueTest msgqueuetest(5);
			if(!msgqueuetest.test())
			{
				throw std::logic_error("MessageQueueTest test fail");
			}
            BOOST_LOG_TRIVIAL(info) << "MessageQueueTest test success";
		}
		if(test_timed_invoker){
			TimedInvokerTest timeinvoketest(5);
			if(!timeinvoketest.test())
			{
				throw std::logic_error("TimedInvokerTest test fail");
			}
            BOOST_LOG_TRIVIAL(info) << "TimedInvokerTest test success";
		}
		if(test_timer_service){
			TimerServiceTest test_case;
			if(!test_case.test())
			{
				throw std::logic_error("TimeServiceTest test fail");
			}
            BOOST_LOG_TRIVIAL(info) << "TimeServiceTest test success";
		}

        BOOST_LOG_TRIVIAL(info) << "section " << section_name << " test success";
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "service test exception:" << ex.what();
        return false;
    }
}



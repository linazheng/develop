#include <functional>
#include <boost/log/trivial.hpp>
#include <unistd.h>
#include "service/timed_invoker_test.h"

TimedInvokerTest::TimedInvokerTest(const int &num): num(num),count(0),count1(0) {
}
TimedInvokerTest::~TimedInvokerTest() {
}
void TimedInvokerTest::handler() {
    count ++;
    //BOOST_LOG_TRIVIAL(info) << "-------------" << count;
}
void TimedInvokerTest::handler1() {
    count1 ++;
    //BOOST_LOG_TRIVIAL(info) << "++++++++++" <<count1;
}

bool TimedInvokerTest::test() {

    zhicloud::service::TimedInvoker timedInvoker1(std::chrono::milliseconds(10),num);
    timedInvoker1.bindHandler(std::bind(&TimedInvokerTest::handler, this));
    timedInvoker1.bindHandler(std::bind(&TimedInvokerTest::handler1, this));
    timedInvoker1.start();

    zhicloud::service::TimedInvoker timedInvoker2(std::chrono::milliseconds(1000), num);
    timedInvoker2.bindHandler(std::bind(&TimedInvokerTest::handler, this));
    timedInvoker2.bindHandler(std::bind(&TimedInvokerTest::handler1, this));
    timedInvoker2.start();

    sleep(num + (0.01 *num)/1 + 1);
    timedInvoker1.stop();
    timedInvoker2.stop();


    return (count == num *2) && (count1 == num *2);
}



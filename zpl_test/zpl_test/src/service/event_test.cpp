#include "service/event_test.h"

#include <boost/log/trivial.hpp>
#include <thread>
#include <unistd.h>

EventTest::EventTest(const int &loop_num) : num(loop_num),count1(0),count2(0){
}
EventTest::~EventTest(){
}


void EventTest:: tester1(){
    for(int i = 0; i < num; i++){
        event1.set();
        //BOOST_LOG_TRIVIAL(info) << "event1 set" ;
        event2.wait();
        //BOOST_LOG_TRIVIAL(info) << "event2 wait" ;
        count1++;
    }
	/*
    event1.set();
    event2.wait();
    */


}
void EventTest::tester2(){
    for(int i = 0; i < num; i++){
        event1.wait();
        //BOOST_LOG_TRIVIAL(info) << "event1 wait" ;
        event2.set();
        //BOOST_LOG_TRIVIAL(info) << "event2 set" ;
        count2++;
    }
	/*
    event1.wait();
    event2.set();
    event2.clear();
    event2.set();
    */

}
bool EventTest::test(){
    thread   thread1(&EventTest::tester1, this);
    thread   thread2(&EventTest::tester2, this);
    thread1.join();
    thread2.join();

    /*sleep(30);
	thread1.detach();
	thread2.detach();*/

	BOOST_LOG_TRIVIAL(info) << "EventTest test finish!";
    return count1 == count2  && count2 == num;
}


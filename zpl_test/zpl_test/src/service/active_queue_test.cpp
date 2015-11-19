#include <exception>
#include <boost/log/trivial.hpp>
#include "active_queue_test.h"
#include "active_queue_event_sender.hpp"

using namespace std;

ActiveQueueTest::ActiveQueueTest()
{
    //ctor
}

ActiveQueueTest::~ActiveQueueTest()
{
    //dtor
}

bool ActiveQueueTest::test(){
    try{
        BOOST_LOG_TRIVIAL(info) << "active queue test begin...";
        {
            ActiveQueueEventSender single(10000000);
            BOOST_LOG_TRIVIAL(info) << "test case:single sender begin...";
            if(!single.test()){
                throw std::logic_error("active queue single sender test fail");
            }
            BOOST_LOG_TRIVIAL(info) << "test case:single sender test success";
        }
//        {
//            ActiveQueueEventSender multi(10000000, 5);
//            if(!multi.test()){
//                throw std::logic_error("active queue multi sender test fail");
//            }
//            BOOST_LOG_TRIVIAL(info) << "active queue multi sender  test success";
//        }
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "active queue test exception:" << ex.what();
        return false;
    }

}

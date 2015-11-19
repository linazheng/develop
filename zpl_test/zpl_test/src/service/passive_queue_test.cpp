#include <exception>
#include <boost/log/trivial.hpp>
#include "passive_queue_test.h"
#include "passive_queue_event_sender.hpp"

using namespace std;

PassiveQueueTest::PassiveQueueTest()
{
    //ctor
}

PassiveQueueTest::~PassiveQueueTest()
{
    //dtor
}

bool PassiveQueueTest::test(){
    try{
        BOOST_LOG_TRIVIAL(info) << "passive queue test begin...";
        size_t event_count(100*10000);
        size_t producer_count(1);
        size_t consumer_count(1);
        string case_name;
        {
            case_name = (boost::format("%d event with %d producer & %d consumer")%event_count %producer_count %consumer_count ).str();

            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            PassiveQueueEventSender test_case(event_count, producer_count, consumer_count);
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        {
            event_count = 20*10000;
            producer_count = 5;
            consumer_count = 3;
            case_name = (boost::format("%d event with %d producer & %d consumer")%event_count %producer_count %consumer_count ).str();

            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            PassiveQueueEventSender test_case(event_count, producer_count, consumer_count);
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        BOOST_LOG_TRIVIAL(info) << "passive queue test success";
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "passive queue test exception:" << ex.what();
        return false;
    }

}

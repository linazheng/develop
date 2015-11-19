#include <boost/log/trivial.hpp>
#include <boost/format.hpp>
#include "timer_service_normal_timer.hpp"
#include "timer_service_clear_timer.hpp"
#include "timer_service_loop_timer.hpp"
#include "timer_service_performance.hpp"
#include "timer_service_capacity.hpp"
#include "service/timer_service_test.h"

using namespace std;

TimerServiceTest::TimerServiceTest(){

}
TimerServiceTest::~TimerServiceTest() {

}
bool TimerServiceTest::test() {
    try{
        bool normal_timer(false);
        bool loop_timer(false);
        bool clear_timer(false);
        bool performance(false);
        bool capacity(true);

        BOOST_LOG_TRIVIAL(info) << "timer service test begin...";
        string case_name;
        if(normal_timer){
            case_name = "normal timer";
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TimerServiceNormalTimer test_case;
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        if(loop_timer){
            case_name = "loop timer";
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TimerServiceLoopTimer test_case;
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        if(clear_timer){
            case_name = "clear timer";
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TimerServiceClearTimer test_case;
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        if(performance){
            case_name = "performance";
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TimerServicePerformance test_case;
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        if(capacity){
            case_name = "capacity";
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TimerServiceCapacity test_case;
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "timer service test exception:" << ex.what();
        return false;
    }
}



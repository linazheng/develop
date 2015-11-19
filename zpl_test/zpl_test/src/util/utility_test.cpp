#include <iostream>
#include "util/utility_test.h"
#include <util/define.hpp>

#include <util/digest.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <boost/log/trivial.hpp>

#include <transaction/base_session.hpp>
#include <transaction/base_task.hpp>
#include <transaction/process_rule.hpp>
#include <transaction/base_manager.hpp>
#include <transport/app_message.h>
#include <transport/command.h>

#include "util/digest_test.h"
#include "util/domain_utility_test.h"
#include "util/generator_test.h"
#include "util/logging_test.h"
#include "util/serial_test.h"



#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <zpl.hpp>

#include <semaphore.h>
#include <time.h>

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;

UtilityTest::UtilityTest()
{
    //ctor
}

UtilityTest::~UtilityTest()
{
    //dtor
}

bool UtilityTest::test()
{
	try{
        string section_name("Util");
        BOOST_LOG_TRIVIAL(info) << "begin test section " << section_name << "...";

		{
			DigestTest digesttest;
			if (!digesttest.test())
			{				
                throw std::logic_error("class Digest test failed");
			}
            BOOST_LOG_TRIVIAL(info) << "class Digest test success";
		}
		{
			GeneratorTest generatortest;
			if (!generatortest.test())
			{				
                throw std::logic_error("class generator test failed");
			}
            BOOST_LOG_TRIVIAL(info) << "class generator test success";
		}
		{
			LoggingTest loggingtest;
			loggingtest.init();
			if (!loggingtest.test())
			{
                throw std::logic_error("logging test failed");
			}
			BOOST_LOG_TRIVIAL(info) << "logging test success";
		}
		{
			SerialTest serialtest;
			if (!serialtest.test())
			{
                throw std::logic_error("Serialize test failed");
			}
			BOOST_LOG_TRIVIAL(info) << "Serialize test success";
		}
		
        BOOST_LOG_TRIVIAL(info) << "section " << section_name << " test success";
		return true;
	}
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "Transaction test exception:" << ex.what();
        return false;
    }

}





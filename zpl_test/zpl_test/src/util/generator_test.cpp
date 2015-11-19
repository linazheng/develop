#include <iostream>
#include "util/generator_test.h"


#include <util/define.hpp>
#include <util/network_utility.h>
#include <util/domain_utility.h>
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


#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <zpl.hpp>

#include <semaphore.h>
#include <time.h>

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;

GeneratorTest::GeneratorTest()
{
    //ctor

}

GeneratorTest::~GeneratorTest()
{
    //dtor
}

bool GeneratorTest::test()
{

	BOOST_LOG_TRIVIAL(info) << boost::format("uuid test generate one[%s], hex false[%s], hex true[%s]")
							%uuid.uuid() %uuid.uuid_hex(false) %uuid.uuid_hex(true);

	BOOST_LOG_TRIVIAL(info) << boost::format("uuid test generate two[%s], hex false[%s], hex true[%s]")
							%uuid.uuid() %uuid.uuid_hex(false) %uuid.uuid_hex(true);

	BOOST_LOG_TRIVIAL(info) << boost::format("uuid test mac addr[%s]")
							%generateMAC();

	BOOST_LOG_TRIVIAL(info) <<"Generator test uuid and hex pass.";
	return true;
}






#include <iostream>
//#include "DigestTest.h"
#include "util/domain_utility_test.h"


#include <util/define.hpp>

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

DomainUtilTest::DomainUtilTest(const string& domain_name, const string& address = "224.6.6.6", const uint16_t& port = 5666)
	:DomainUtil(domain_name, address, port)
{
    //ctor

	BOOST_LOG_TRIVIAL(info) << boost::format("bulid DomainUtilTest name[%s], addr[%s], port[%d]")
							%domain_name %address %(uint32_t)port;
}

DomainUtilTest::~DomainUtilTest()
{
    //dtor
}

bool DomainUtilTest::DomainCliTest()
{
	DomainUtil.bindHandler(DomainBindTest);
	DomainUtil.bindHandler(DomainBindTest);

	DomainUtil.start();
	DomainUtil.query();
	sleep(15);
	DomainUtil.stop();

	return true;
}


bool DomainUtilTest::DomainSrvTest()
{
	DomainUtil.addService("dataserver", "224.6.6.6", 1234);
	DomainUtil.start();
	DomainUtil.publish();
	sleep(30);
	DomainUtil.stop();
    return true;
}

void DomainBindTest(const string& service_name,
							const string& service_ip,
							const uint16_t& serivce_port,
							const string& request_ip)
{
	BOOST_LOG_TRIVIAL(info) << boost::format("DomainBindTest name[%s], addr[%s], port[%d], request ip[%d]")
							%service_name %service_ip %(uint32_t)serivce_port %request_ip;
    return;
}





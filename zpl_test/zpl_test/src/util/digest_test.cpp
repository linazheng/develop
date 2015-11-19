#include <iostream>
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


#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <zpl.hpp>

#include <semaphore.h>
#include <time.h>
#include "util/digest_test.h"

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;



bool DigestTest::test(){
	uiCrc = digestObj.crc32("wangli DigestTest crc");

	BOOST_LOG_TRIVIAL(info) << boost::format("DigestTest test crc:%d")%uiCrc;

	BOOST_LOG_TRIVIAL(info) << boost::format("DigestTest test sha1_hex:%s")%digestObj.sha1_hex("wangli DigestTest sha1_hex");
	BOOST_LOG_TRIVIAL(info) <<"Digest test crc and sha1hex pass.";
    return true;
}





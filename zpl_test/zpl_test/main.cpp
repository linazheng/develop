#include <iostream>
#include <exception>
#include "util/utility_test.h"
#include "service/service_unify_test.h"
#include "transaction/transaction_unify_test.h"
#include "transport/transport_unify_test.h"

#include <util/logger.h>
#include <util/logging.h>
#include <util/lc/singleton.h>
#include <boost/log/trivial.hpp>

using namespace std;

int main()
{
    string section_name("build up");
    try{
        bool service(true);
        bool transport(false);
        bool transaction(false);
        bool utility(true);
//        zhicloud::util::initialLogging();
//        zhicloud::util::addFileAppender(".", "test", 40960000);
        if(utility){
			UtilityTest utilitytest;
			if (!utilitytest.test())
			{
				throw std::logic_error("namespace util test failed");
			}
    	}

        if(service){
            ServiceUnifyTest serviceunify;
            if(!serviceunify.test()){
                throw std::logic_error("service test fail");
            }
        }
        if(transport){
            TransportUnifyTest test_case;
            if(!test_case.test()){
                throw std::logic_error("transport test fail");
            }
        }
		if(transaction){
			TransactionUnifyTest transunifytest;
			if (!transunifytest.test())
			{
				throw std::logic_error("namespace transaction test failed");
			}
		}
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "test exception in section " << section_name << ", message:" << ex.what();
    }

	/*
      //zhicloud::util::finishLogging();

	sleep(5);
	*/

    return 0;
}

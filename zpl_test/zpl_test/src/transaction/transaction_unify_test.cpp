#include <iostream>
#include <thread>
#include <chrono>
#include <boost/log/trivial.hpp>
#include <boost/random.hpp>
#include <boost/random/random_device.hpp>

#include <zpl.hpp>

#include "transaction/transaction_unify_test.h"


using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;

TransactionUnifyTest::TransactionUnifyTest()
{

}
TransactionUnifyTest::~TransactionUnifyTest()
{

}

bool TransactionUnifyTest::test()
{
	try{
        string section_name("Transaction");
        BOOST_LOG_TRIVIAL(info) << "begin test section " << section_name << "...";
		{
			BaseManagerTest basemanagertest;
			if (!basemanagertest.test_recombination9())
			{
                throw std::logic_error("basemanagertest test recombination session failed");
			}
            BOOST_LOG_TRIVIAL(info) << "basemanagertest test recombination session success";
		}
        BOOST_LOG_TRIVIAL(info) << "section " << section_name << " test success";
		return true;

	}
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "Transaction test exception:" << ex.what();
        return false;
    }





	/*
	if (!basemanagertest.test())
	{
		BOOST_LOG_TRIVIAL(warning) << "basemanagertest test failed!";
		printf("basemanagertest test failed!\n");
		return false;
	}
	printf("basemanagertest test passed!\n");

	if (!basemanagertest.test_allocTrans())
	{
		BOOST_LOG_TRIVIAL(warning) << "basemanagertest test alloc and dealloc transaction failed!";
		printf("basemanagertest test alloc and dealloc transaction failed!\n");
		return false;
	}
	printf("basemanagertest test alloc and dealloc transaction passed!\n");

	if (!basemanagertest.test_startTrans())
	{
		BOOST_LOG_TRIVIAL(warning) << "basemanagertest test start transaction failed!";
		printf("basemanagertest test start transaction failed!\n");
		return false;
	}
	printf("basemanagertest test start transaction passed!\n");

	if (!basemanagertest.test_processMessage())
	{
		BOOST_LOG_TRIVIAL(warning) << "basemanagertest test process message failed!";
		printf("basemanagertest test process message failed!\n");
		return false;
	}
	printf("basemanagertest test process message passed!\n");

	if (!basemanagertest.test_recombination9())
	{
		BOOST_LOG_TRIVIAL(warning) << "basemanagertest test recombination session failed!";
		printf("basemanagertest test recombination session failed!\n");
		return false;
	}
	printf("basemanagertest test recombination session passed!\n");
	*/
}




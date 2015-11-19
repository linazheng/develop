#include <iostream>
#include "util/logging_test.h"

#include <util/define.hpp>
#include <util/network_utility.h>
#include <util/domain_utility.h>
#include <util/logger.h>
#include <util/logging.h>
#include <util/lc/logger.h>
#include <util/lc/logging.h>
#include <util/lc/singleton.h>
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
#include <boost/filesystem.hpp>
#include <sys/stat.h>

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;
using namespace boost::filesystem;

LoggingTest::LoggingTest()
{
    //ctor
	logger = getLogger("LogTester");

	logger->info("<LogTester> service started.");
}

LoggingTest::~LoggingTest()
{
    //dtor
}
void LoggingTest::init()
{
	bIsRunning = true;

	if (true != initialLogging())
	{
		BOOST_LOG_TRIVIAL(info) <<"init logging failed.";
	} else {
	    BOOST_LOG_TRIVIAL(info) <<"init logging success.";
	}

	if(!lc::initialLogging()) {
        cout << "error in lc::initialLogging" << endl;
	}

//	if (true != addFileAppender("/var/zhicloud/mylog", "wllog", 512))
//	{
//		BOOST_LOG_TRIVIAL(info) <<"addFileAppender failed.";
//	}
//	//BOOST_LOG_TRIVIAL(info) <<"addFileAppender success.";
//
//	if (true != setCollector("/var/zhicloud/mylog", 512))
//	{
//		BOOST_LOG_TRIVIAL(info) <<"setCollector failed.";
//	}
	//BOOST_LOG_TRIVIAL(info) <<"setCollector success.";


	//BOOST_LOG_TRIVIAL(info) <<"LoggingTest init finish.";
	//printf("LoggingTest init finish ..........\n");
    return;
}

namespace {

bool test_new_logger()
{
    setCollector("/var/zhicloud/old_log", 50000000);
    addFileAppender("/var/zhicloud/old_log", "old_logger_prefix", 100000);
    zhicloud::util::logger_type old_logger = getLogger("old", level_info);
    lc::setCollector("/var/zhicloud/new_log", 50000000);
    if(!lc::addFileAppender("/var/zhicloud/new_log", "new_logger_prefix", 100000)) {
        return false;
    }

    lc::logger_type new_logger = lc::getLogger("new", lc::level_info);
    uint32_t loop_count = 0;

    while(true)
    {
        if(++loop_count > 30) {
            break;
        }

        struct timeval tv_begin_1;
        gettimeofday(&tv_begin_1, NULL);
        uint64_t begin_time_1 = (uint64_t)tv_begin_1.tv_sec * 1000000 + tv_begin_1.tv_usec;
        for(int i = 0; i != 1000; ++i)
        {
            old_logger->info(boost::format("this is long msg very long this is my lc log test: %s") % "abc");
        }

        struct timeval tv_end_1;
        gettimeofday(&tv_end_1, NULL);
        uint64_t end_time_1 = (uint64_t)tv_end_1.tv_sec * 1000000 + tv_end_1.tv_usec;
        uint64_t diff_time_1 = end_time_1 - begin_time_1;
        cout << "diff_time_1: " << diff_time_1 / 1000 << " msec" << endl;

        struct timeval tv_begin_2;
        gettimeofday(&tv_begin_2, NULL);
        uint64_t begin_time_2 = (uint64_t)tv_begin_2.tv_sec * 1000000 + tv_begin_2.tv_usec;
        for(int i = 0; i != 1000; ++i)
        {
            new_logger->info(boost::format("this is long msg very long this is my lc log test: %s") % "abc");
        }

        struct timeval tv_end_2;
        gettimeofday(&tv_end_2, NULL);
        uint64_t end_time_2 = (uint64_t)tv_end_2.tv_sec * 1000000 + tv_end_2.tv_usec;
        uint64_t diff_time_2 = end_time_2 - begin_time_2;
        cout << "diff_time_2: " << diff_time_2 / 1000 << " msec" << endl << endl;
        sleep(1);
    }

    finishLogging();

    struct timeval tv_begin;
    gettimeofday(&tv_begin, NULL);
    uint64_t begin_time = (uint64_t)tv_begin.tv_sec * 1000000 + tv_begin.tv_usec;
    lc::finishLogging(); //new logger finishLogging();
    struct timeval tv_end;
    gettimeofday(&tv_end, NULL);
    uint64_t end_time = (uint64_t)tv_end.tv_sec * 1000000 + tv_end.tv_usec;
    uint64_t diff_time = end_time - begin_time;
    cout << "diff_time in lc::finishLoggin(): " << diff_time / 1000 << " msec" << endl;

    return true;
}

}

bool LoggingTest::test()
{
    if(!test_new_logger()) {
        return false;
    }

//	int idx = 0;
//
//	while (idx < 10)
//	{
//		for (int i = 0 ; i < 5; i++)
//		{
//			BOOST_LOG_TRIVIAL(info) <<"wangli test log info................";
//		}
//
//		if (true != setCollector("/var/zhicloud/mylog", 512))
//		{
//			printf("test setCollector failed.\n");
//			return false;
//		}
//
//		sleep(1);
//		idx++;
//	}
//	sleep(3);
//	/*if (true != finishLogging())
//	{
//		BOOST_LOG_TRIVIAL(warning) <<"finish logging failed.";
//
//		return false;
//	}
//	sleep(3);*/
//
//	directory_iterator end;
//	for (directory_iterator pos("/var/zhicloud/mylog"); pos != end; ++pos)
//	{
//        if (is_regular_file(pos->status()))
//        {
//            filenames.push_back(pos->path().string());
//        }
//	}
//
//	int filesize = 0;
//	for ( int i = 0 ; i < filenames.size(); i++)
//	{
//		//BOOST_LOG_TRIVIAL(info) << boost::format("file %d:[%s]") %i %filenames[i].c_str() ;
//		filesize = file_size(filenames[i].c_str());
//		//BOOST_LOG_TRIVIAL(info) << boost::format("file %d size is %d") %i %filesize;
//		if ( 512 < filesize)
//		{
//			BOOST_LOG_TRIVIAL(warning) <<"limit log size failed!.";
//		    return false;
//		}
//	}

	BOOST_LOG_TRIVIAL(info) <<"Logging test all pass.";
	return true;
}





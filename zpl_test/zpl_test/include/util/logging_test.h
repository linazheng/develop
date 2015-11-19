#ifndef LOGTEST_H
#define LOGTEST_H

#include <util/logger.h>
#include <util/logging.h>

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp> 
#include <iostream>   
#include <vector>  
#include <boost/filesystem.hpp>  

using namespace zhicloud::util;
using namespace std;
using boost::asio::ip::udp;

class LoggingTest
{
    public:
        LoggingTest();
        virtual ~LoggingTest();
		void init();
        bool test();
	public:
		bool bIsRunning;
    protected:
    private:
		logger_type logger;
		vector<string> filenames;
		
};



#endif // LOGTEST_H
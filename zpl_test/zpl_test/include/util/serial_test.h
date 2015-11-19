#ifndef SERIALTEST_H
#define SERIALTEST_H

#include <util/serialize.h>
#include <util/generator.h>

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp>

using namespace zhicloud::util;
using namespace std;
using boost::asio::ip::udp;

class SerialTest
{
    public:
        SerialTest();
        virtual ~SerialTest();
		void init();
        bool test();
	public:
		Generator uuid;
    protected:
    private:
		
};



#endif // SERIALTEST_H

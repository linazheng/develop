#ifndef UUIDTEST_H
#define UUIDTEST_H

#include <util/generator.h>

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp>

using namespace zhicloud::util;
using namespace std;
using boost::asio::ip::udp;

class GeneratorTest
{
    public:
        GeneratorTest();
        virtual ~GeneratorTest();
        bool test();
    protected:
    private:
		Generator uuid;
		
};



#endif // DOMAINTEST_H

#include "transport/packet_handler_test.h"
#include <string>
#include <boost/log/trivial.hpp>
#include <exception>
#include "transport/packet_handler_client_server.hpp"


#include <stdio.h>
#include <sys/types.h>
#include <ifaddrs.h>
#include <netinet/in.h>

#include <arpa/inet.h>

using namespace std;

PacketHandlerTest::PacketHandlerTest(const string& ip)
{
	this->IPv4 =ip;
}

PacketHandlerTest::~PacketHandlerTest()
{

}

bool PacketHandlerTest::test()
{
    try{
        BOOST_LOG_TRIVIAL(info) << "packet handler test begin...";
        size_t pkg_count(10*10000);
        size_t pkg_size(1024);
        uint16_t port(5600);
        string case_name("local client&server");
        {
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            PacketHandlerClientServer test_case(pkg_count, pkg_size, this->IPv4, port);
            if(!test_case.test()){
                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        BOOST_LOG_TRIVIAL(info) << "packet handler test success";
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "packet handler test exception:" << ex.what();
        return false;
    }
}

/*const string& PacketHandlerTest::getIP()
{
	struct ifaddrs * ifAddrStruct=NULL;
	struct ifaddrs * ifa=NULL;
	void * tmpAddrPtr=NULL;

	string ip("172.16.2.247");

	getifaddrs(&ifAddrStruct);
	for (ifa = ifAddrStruct; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr) {
            continue;
        }
        if (ifa->ifa_addr->sa_family == AF_INET)
		{ // check it is IP4
            // is a valid IP4 Address
            tmpAddrPtr=&((struct sockaddr_in *)ifa->ifa_addr)->sin_addr;
            char addressBuffer[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, tmpAddrPtr, addressBuffer, INET_ADDRSTRLEN);

			string ip4(addressBuffer);
			if ( ip4.compare("127.0.0.0") )
			{
				continue;
			}
			freeifaddrs(ifAddrStruct);
			BOOST_LOG_TRIVIAL(info) << boost::format("PacketHandlerTest localhost IPv4 is [%s]")%ip4 ;

			return ip4;
        }
    }
    if (ifAddrStruct!=NULL) freeifaddrs(ifAddrStruct);

	return ip;
}*/






#include <iostream>
#include <functional>
#include <boost/log/trivial.hpp>
#include <unistd.h>
#include "service/node_service_test.h"

#include <service/node_service.h>


using namespace std;
using namespace zhicloud::service;
using zhicloud::util::ServiceType;

NodeServiceTest::NodeServiceTest()
{
}
NodeServiceTest::~NodeServiceTest() {
}

void NodeServiceTest::srvtest()
{
	NodeService server(ServiceType::data_server, "dataserver", "example", "172.16.2.247", 5600 + (uint32_t)ServiceType::data_server, 200, "224.6.6.6", 5222, "wangliserver");
	BOOST_LOG_TRIVIAL(info) << "NodeServiceTest srvtest before start";
	server.start();
	BOOST_LOG_TRIVIAL(info) << "NodeServiceTest srvtest after start";
}

void NodeServiceTest::clitest()
{
	NodeService client(ServiceType::manage_terminal, "client", "wltest", "172.16.2.247", 5600 + (uint32_t)ServiceType::manage_terminal, 200, "224.6.6.6", 5223, "wangliclient");
    BOOST_LOG_TRIVIAL(info) << "NodeServiceTest clitest before start";
	client.start();
	BOOST_LOG_TRIVIAL(info) << "NodeServiceTest clitest after start";
    client.connectEndpoint("data_server_wanglitest", ServiceType::data_server, "172.16.2.247", 5600);
    BOOST_LOG_TRIVIAL(info) << "NodeServiceTest clitest connectEndpoint";
}

bool NodeServiceTest::test()
{
    thread   thread1(&NodeServiceTest::srvtest, this);
    thread   thread2(&NodeServiceTest::clitest, this);

    thread1.join();
    thread2.join();

	sleep(10);

    return true;
}



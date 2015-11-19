#ifndef PACKET_HANDLER_TEST_H__
#define PACKET_HANDLER_TEST_H__


#include <string>

using namespace std;


class PacketHandlerTest{
public:
    PacketHandlerTest(const string& ip);
    ~PacketHandlerTest();
    bool test();

private:
	
	string IPv4;

};

#endif // PACKET_HANDLER_TEST_H__

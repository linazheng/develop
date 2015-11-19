#include "transport/transport_unify_test.h"
#include "transport/packet_handler_test.h"
#include "transport/transporter_test.h"

#include <iostream>
#include <string>

#include <boost/log/trivial.hpp>
#include <exception>

using namespace std;

TransportUnifyTest::TransportUnifyTest()
{

}

TransportUnifyTest::~TransportUnifyTest()
{

}

bool TransportUnifyTest::test()
{
    try{
        string section_name("transport");
        BOOST_LOG_TRIVIAL(info) << "begin test section " << section_name << "...";

        /*{
			string server_ip;
			cout<<"PacketHandler test begin, please input server ip:"<<endl;
			cin>>server_ip;

			cout<<"ip is "<<server_ip<<endl;
            PacketHandlerTest test(server_ip);
            if(!test.test()){
                throw std::logic_error("packet handler test fail");
            }
        }*/
        {
			string server_ip;
			cout<<"Transporter test begin, please input server ip:"<<endl;
			cin>>server_ip;

			cout<<"ip is "<<server_ip<<endl;
            TransporterTest test(server_ip);
            if(!test.test()){
                throw std::logic_error("transporter test fail");
            }
        }
        BOOST_LOG_TRIVIAL(info) << "section " << section_name << " test success";
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "transport test fail:" << ex.what();
        return false;
    }
}




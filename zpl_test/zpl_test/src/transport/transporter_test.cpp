#include "transport/transporter_test.h"
#include <string>
#include <boost/log/trivial.hpp>
#include <boost/format.hpp>
#include <exception>
#include "transport/transporter_client.hpp"
#include "transport/transporter_server.hpp"

using namespace std;

TransporterTest::TransporterTest(const string& ip)
{
	this->IPv4 = ip;
}

TransporterTest::~TransporterTest()
{

}

bool TransporterTest::test()
{
    try{
        BOOST_LOG_TRIVIAL(info) << "transporter test begin...";
        size_t pkg_count(10*10000);
        size_t pkg_size(1024);
		
        //string server_ip("172.16.2.247");
        uint16_t port(5600);
        string case_name("local client&server");
        {
            BOOST_LOG_TRIVIAL(info) << boost::format("test case:%s begin..") % case_name;
            TransporterServer server(this->IPv4, port);
            if(!server.build()){
                throw std::logic_error((boost::format("build up server with '%s' fail") % this->IPv4).str());
            }

            TransporterClient client(pkg_count, pkg_size, this->IPv4, this->IPv4, port);
            if(!client.build()){
                throw std::logic_error((boost::format("build up client with '%s' fail") % this->IPv4).str());
            }
            client.waitConnected(0);
            size_t timeout(5);
            if(!server.waitResult(timeout)){
                throw std::logic_error((boost::format("test case: %s test fail") % case_name).str());
            }
//            PacketHandlerClientServer test_case(pkg_count, pkg_size, server_ip, port);
//            if(!test_case.test()){
//                throw std::logic_error((boost::format("test case:%s failed") % case_name).str());
//            }
            BOOST_LOG_TRIVIAL(info) << "test case: " << case_name << " test success";
        }
        BOOST_LOG_TRIVIAL(info) << "transporter test success";
        return true;
    }
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "transporter test exception:" << ex.what();
        return false;
    }
}


//#include <transaction/base_session.hpp>
//#include <transaction/base_task.hpp>
//#include <transaction/process_rule.hpp>
//#include <transaction/base_manager.hpp>
//#include <transport/app_message.h>
//#include <transport/command.h>
//
//#include <util/define.hpp>
//#include <iostream>
//#include <thread>
//#include <chrono>
//#include <boost/log/trivial.hpp>
//#include <boost/random.hpp>
//#include <boost/random/random_device.hpp>
//#include <boost/bind.hpp>
//#include <boost/signals2.hpp>
//#include <zpl.hpp>
//
//#include <semaphore.h>
//#include <time.h>
//
//#include "transport/transporter_test.h"
//
//using namespace std;
//using namespace zhicloud::transaction;
//using namespace zhicloud::transport;
//using namespace zhicloud::util;
//using std::string;
//using std::shared_ptr;
//
//
//ttp_client::ttp_client():cliTrsp("client", 1, 1)
//{
//	msg_send = 0;
//}
//
//int ttp_client::init(const string& client_ip,
//					int channel,
//					int message_count,
//					int message_size,
//					bool bIsBatch)
//{
//    this->channel = channel;
//    this->message_count = message_count;
//    this->message_size = message_size;
//	msg_send = 0;
//	msg_recv = 0;
//	bIsBatch = bIsBatch;
//
//	if(!cliTrsp.bind(client_ip, 5603, 200))
//	{
//		BOOST_LOG_TRIVIAL(info) << "clinet bind failed!";
//		return -1;
//	}
//	cliTrsp.bindConnectedHandler(boost::bind(&ttp_client::CliConnectedHandler, this, _1, _2));
//	cliTrsp.bindDisconnectedHandler(boost::bind(&ttp_client::CliDisconnectedHandler, this, _1, _2));
//	cliTrsp.bindMessageHandler(boost::bind(&ttp_client::CliMsgHandler, this, _1, _2));
//
//	cliTrsp.start();
//
//	return 0;
//}
//
//bool ttp_client::CliConnect(const string& server_ip, int server_port)
//{
//	uint32_t i;
//	for (i = 0; i < this->channel; i++)
//	{
//		bool ret = cliTrsp.tryConnect("server", server_ip, server_port);
//		if(!ret)
//		{
//			BOOST_LOG_TRIVIAL(info) << boost::format("channel:[%d],tryconnect failed")%i;
//			return false;
//		}
//	}
//
//    return true;
//}
//bool ttp_client::JudgeMessage(const unsigned long &send, const unsigned long &recv)
//{
//	BOOST_LOG_TRIVIAL(info) << boost::format("JudgeMessage send[%d] recv[%d]")%send %recv;
//    return (send==recv);
//}
//bool ttp_client::TestBatch()
//{
//	bool ret = false;
//
//    this->init("172.16.2.247", 1, 5000, 4096, true);
//
//	this->CliConnect("172.16.2.247", 5600);
//
//	sleep(10);
//	if (JudgeMessage(this->msg_send, this->msg_recv))
//	{
//	    ret = true;
//	}
//	BOOST_LOG_TRIVIAL(info) <<"ttp_client TestBatch stop.";
//	this->cliTrsp.stop();
//    return ret;
//}
//
//bool ttp_client::TestNormal()
//{
//	bool ret = false;
//    this->init("172.16.2.247", 1, 5000, 4096, false);
//	this->CliConnect("172.16.2.247", 5600);
//
//	sleep(10);
//	if (JudgeMessage(this->msg_send, this->msg_recv))
//	{
//	    ret = true;
//	}
//
//    return ret;
//}
//void ttp_client::Reset()
//{
//    msg_send = 0;
//	msg_recv = 0;
//}
//
//bool ttp_client::Test()
//{
//	if (!this->TestNormal())
//	{
//		BOOST_LOG_TRIVIAL(warning) << "ttp_client TestNormal failed!";
//		this->TransStop();
//		return false;
//	}
//	Reset();
//	if (!this->TestBatch())
//	{
//		BOOST_LOG_TRIVIAL(warning) << "ttp_client TestBatch failed!";
//		this->TransStop();
//		return false;
//	}
//
//	this->TransStop();
//    return true;
//}
//
//void ttp_client::TransStart()
//{
//    string formation;
//	int idx = 0;
//	while (idx < this->message_size)
//	{
//	    formation += "1";
//		idx++;
//	}
//
//	//BOOST_LOG_TRIVIAL(info) << boost::format("client trans msg size: %d")%formation.length();
//
//	AppMessage event(AppMessage::message_type::EVENT, zhicloud::util::EventEnum::channel_connected);
//	event.setString(zhicloud::util::ParamEnum::filename, formation);
//
//	for ( int i = 0 ; i < message_count; i++)
//	{
//		datagram_list.push_back(event);
//	}
//	//start
//	AppMessage start(AppMessage::message_type::REQUEST, zhicloud::util::RequestEnum::start_statistic);
//	cliTrsp.sendMessage(session_cli.front(), start);
//
//
//	/*if (bIsBatch)
//	{
//		BatchSend();
//	}
//	else
//	{
//		Send();
//	}*/
//
//	Send();
//	sleep(5);
//	BatchSend();
//
//	return;
//}
//
//void ttp_client::TransStop()
//{
//
//	AppMessage stop(AppMessage::message_type::REQUEST,zhicloud::util::RequestEnum::stop_statistic);
//	//stop.setUInt(zhicloud::util::ParamEnum::sent_bytes, total_length);
//	//stop.setUInt(zhicloud::util::ParamEnum::sent_packets, total_message);
//	cliTrsp.sendMessage(session_cli.front(),stop);
//}
//
//void ttp_client::Send( )
//{
//	BOOST_LOG_TRIVIAL(info) << "client Send normal";
//    for (AppMessage &msg:datagram_list)
//    {
//		cliTrsp.sendMessage(session_cli.front(),msg);
//		msg_send++;
//    }
//
//	BOOST_LOG_TRIVIAL(info) << boost::format("client Send msg num:%d") %msg_send;
//}
//
//void ttp_client::BatchSend( )
//{
//	BOOST_LOG_TRIVIAL(info) << "client Send batchSend";
//	cliTrsp.batchSend(session_cli.front(), datagram_list);
//	msg_send += this->message_count;
//}
//
//ttp_server::ttp_server()
//	:srvTrsp("server", 1, 1)
//{
//    total_message = 0;
//	first_packet = 0;
//	last_packet = 0;
//	channel = 0;
//	ulSrvMsgNum = 0;
//}
//
//bool ttp_server::init(const string& server_ip, int channel)
//{
//    this->channel = channel;
//
//	if (!srvTrsp.bind(server_ip, 5600, 200))
//	{
//		BOOST_LOG_TRIVIAL(info) << "ttp_server init bind failed!";
//		return false;
//	}
//
//	srvTrsp.bindConnectedHandler(boost::bind(&ttp_server::SrvConnectedHandler, this, _1, _2));
//	srvTrsp.bindDisconnectedHandler(boost::bind(&ttp_server::SrvDisconnectedHandler, this, _1, _2));
//	srvTrsp.bindMessageHandler(boost::bind(&ttp_server::SrvMsgHandler, this, _1, _2));
//
//	if (!srvTrsp.start())
//	{
//		BOOST_LOG_TRIVIAL(info) << "ttp_server init start failed!";
//		return false;
//	}
//	BOOST_LOG_TRIVIAL(info) << "ttp_server init start success!";
//
//	return true;
//}
//
//
//void ttp_server::SrvConnectedHandler(const string& str, const Transporter::session_id_type& session_id)
//{
//     //printf("remote node '%s'[%d] connected",str.c_str(), (unsigned int)session_id);
//	 //BOOST_LOG_TRIVIAL(info) << "SrvConnectedHandler start";
//     this->sessionSrv.push_back(session_id);
//
//}
//void ttp_server::SrvDisconnectedHandler(const string& remote_name, const Transporter::session_id_type& session_id)
//{
//     //printf("remote node '%s'[%d] disconnected",remote_name.c_str(), (unsigned int)session_id);
//}
//
//void ttp_server::SrvMsgHandler(AppMessage& message, const Transporter::session_id_type& session_id)
//{
//    if (message.id == (uint32_t)zhicloud::util::RequestEnum::start_statistic)
//    {
//        BOOST_LOG_TRIVIAL(info) << "SrvMsgHandler start_statistic start_statistic.";
//    }
//	if (message.id == (uint32_t)zhicloud::util::RequestEnum::stop_statistic)
//	{
//        BOOST_LOG_TRIVIAL(info) << "SrvMsgHandler recv stop statistic.";
//
//		AppMessage response(AppMessage::message_type::RESPONSE,zhicloud::util::RequestEnum::stop_statistic);
//		this->srvTrsp.sendMessage(this->sessionSrv.front(), response);
//	}
//	if (message.id == (uint32_t)zhicloud::util::EventEnum::channel_connected)
//	{
//        //BOOST_LOG_TRIVIAL(info) << "SrvMsgHandler recv channel_connected msg.";
//		this->ulSrvMsgNum++;
//		AppMessage response(AppMessage::message_type::RESPONSE, zhicloud::util::EventEnum::channel_connected);
//		this->srvTrsp.sendMessage(this->sessionSrv.front(), response);
//	}
//}
//
//
//
//void ttp_client::CliConnectedHandler(const string& str, const Transporter::session_id_type& type)
//{
//    this->session_cli.push_back(type);
//    if(this->channel == this->session_cli.size())
//    {
//        sleep(1);
//		BOOST_LOG_TRIVIAL(info) << "transporter client connected.";
//        this->TransStart();
//    }
//}
//
//void ttp_client::CliDisconnectedHandler(const string&, const Transporter::session_id_type&)
//{
//    //printf("DisconnectedHandler\n");
//	BOOST_LOG_TRIVIAL(info) << "transporter client disconnected.";
//}
//
//void ttp_client::CliMsgHandler(AppMessage& message, const Transporter::session_id_type& type)
//{
//    if(message.id == (uint32_t)zhicloud::transport::AppMessage::request_id_type::stop_statistic)
//    {
//		bool ret = this->cliTrsp.tryDisconnect(this->session_cli.front());
//		if(ret)
//		{
//			BOOST_LOG_TRIVIAL(info) << "try disconnect success";
//		}
//    }
//	if (message.id == (uint32_t)zhicloud::util::EventEnum::channel_connected)
//	{
//	    msg_recv++;
//	}
//}
//
//
//
//
//
//

#include <transaction/base_session.hpp>
#include <transaction/base_task.hpp>
#include <transaction/process_rule.hpp>
#include <transaction/base_manager.hpp>
#include <util/define.hpp>
#include <iostream>
#include <thread>
#include <chrono>
#include <boost/log/trivial.hpp>
#include "transaction/base_manager_test.h"
#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <vector>


using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;

boost::random::mt19937 gen;

/*enum class State:uint32_t
{
    initial = 0,
    query = 1,
    observer = 2,
    finish = 0xFFFF,
};*/

enum class State:uint32_t
{
    initial = 0,
    stateOne = 1,
	stateTwo = 2,
	stateThree = 3,
	stateFour = 4,
    finish = 0xFFFF,
};

enum class TaskType:uint32_t
{
    invalid = 0,
    create_host = 3,
    delete_host = 1,
};

int my_max_session = 1024;
int my_thread_count = 2;

class UglySession:public BaseSession< TaskType>{
    public:
        UglySession(const session_id_type& id):BaseSession< TaskType> (id),step_num(0)
        {

        }
        UglySession():UglySession(0)
        {}
        UglySession(UglySession&& other)
        {
            step_num= std::move(other.step_num);
        }
        uint64_t step_num;
};

typedef UglySession session_type;
typedef ProcessRule< session_type > rule_type;

class Proxy{
public:
	bool success;
    Proxy(){
        logger = getLogger("Proxy");
		success = true;
    }
    bool sendMessage(AppMessage& msg, const string& receiver){
        BOOST_LOG_TRIVIAL(info) << boost::format("sendMessage called, msg:%d, receiver '%s'")
                     %msg.id %receiver;
        return true;
    }
    bool putMessage(const AppMessage& msg){
        BOOST_LOG_TRIVIAL(info) << boost::format("sendMessageToSelf called, msg:%d")
                     %msg.id;
        return true;
    }
    bool sendToDomainServer(AppMessage& msg){
        BOOST_LOG_TRIVIAL(info) << boost::format("sendToDomainServer called, msg:%d")
                     %msg.id;
        return true;
    }
    int32_t setTimer(const uint32_t& interval, const uint32_t& session_id){
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]setTimer called, interval:%d")
                     %session_id %interval;
        return 1;
    }
    int32_t setLoopTimer(const uint32_t& interval, const uint32_t& session_id){
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]setLoopTimer called, interval:%d")
                     %session_id %interval;
        return 1;
    }
    bool clearTimer(const int32_t& timer_id){
        BOOST_LOG_TRIVIAL(info) << boost::format("clearTimer called, timer_id:%d")
                     %timer_id;
        return true;
    }
    private:
        logger_type logger;
};

typedef BaseTask< session_type, Proxy > T;

class CreateHost:public BaseTask< UglySession, Proxy >
{
public:
	bool success;
	Proxy* ch_proxy;

    CreateHost(Proxy* p_proxy):T(TaskType::create_host, "CreateHost", (uint32_t)RequestEnum::create_host, p_proxy)
    {
    	uint32_t stateOne;
		uint32_t stateTwo;

        addState("stQuery", stateOne);
		addState("observer", stateTwo);

		p_proxy->success = true;
		ch_proxy = p_proxy;

        addTransferRule((uint32_t)State::initial, AppMessage::message_type::RESPONSE, (uint32_t)RequestEnum::query_host,
                        rule_type::Result::any, boost::bind(&CreateHost::onstateone, this, _1, _2), (uint32_t)State::stateOne);
		addTransferRule((uint32_t)State::stateOne, AppMessage::message_type::EVENT, (uint32_t)RequestEnum::join_domain,
						rule_type::Result::any, boost::bind(&CreateHost::onstatetwo, this, _1, _2), (uint32_t)State::stateTwo);

        addTransferRule(stateTwo, AppMessage::message_type::EVENT, (uint32_t)EventEnum::timeout,
        		        rule_type::Result::any, boost::bind(&CreateHost::onstatethree, this, _1, _2), (uint32_t)State::finish);

    }
    virtual void invokeSession(session_type& session) override{
		current_state = (uint32_t)State::initial;
        /*BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]recv CreateHost request, step_num %d")
                     %session.getSessionID() %current_state;*/
		//p_proxy->success = true;
    }

    void onEvent(AppMessage& event, session_type& session){
        session.step_num++;
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]event received, step_num %d, event id %d")
                     %session.getSessionID() %session.step_num %event.id ;

    }
    void onTimeout(AppMessage& event, session_type& session)
    {
        session.step_num++;
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]CreateHost onTimeout, step_num %d ")
                     %session.getSessionID() %session.step_num;
    }

    void onstateone(AppMessage& event, session_type& session){

		try{
	    	//current_state++;
			if ((uint32_t)State::initial != session.getCurrentState())
			{
				ch_proxy->success = false;
                throw std::logic_error((boost::format("[%08X]current state err on state one, current state: %d")
									%session.getSessionID() %session.getCurrentState()).str());
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]CreateHost one, current state %d, event id %d")
						 %session.getSessionID() %current_state %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "CreateHost task exception:" << ex.what();
		}

    }
    void onstatetwo(AppMessage& event, session_type& session){

		try{
	    	//current_state++;
			if ((uint32_t)State::stateOne!= session.getCurrentState())
			{
				ch_proxy->success = false;
                throw std::logic_error((boost::format("[%08X]current state err on state two, current state: %d")
									%session.getSessionID() %session.getCurrentState()).str());
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]CreateHost two, current state %d, event id %d")
						 %session.getSessionID() %current_state %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "CreateHost task exception:" << ex.what();
		}

    }

    void onstatethree(AppMessage& event, session_type& session){

		try{
	    	//current_state++;
			if ((uint32_t)State::stateTwo!= session.getCurrentState())
			{
				ch_proxy->success = false;
                throw std::logic_error((boost::format("[%08X]current state err on state three, current state: %d")
									%session.getSessionID() %session.getCurrentState()).str());
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]CreateHost three, current state %d, event id %d")
						 %session.getSessionID() %current_state %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "CreateHost task exception:" << ex.what();
		}

    }
    virtual void onTerminate(session_type& session) override
    {
        session.step_num++;
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]terminated, step_num %d ")
                     %session.getSessionID() %session.step_num;
    }

private:
	uint32_t current_state;
};

class DeleteHost:public T
{
public:
	Proxy* dh_proxy;

    DeleteHost(Proxy* p_proxy):T(TaskType::delete_host, "DeleteHost", (uint32_t)RequestEnum::delete_host, p_proxy)
    {

    	uint32_t stateOne;
		uint32_t stateTwo;
		uint32_t stateThree;
		uint32_t stateFour;
        addState("stateOne", stateOne);
		addState("stateTwo", stateTwo);
		addState("stateThree", stateThree);
		addState("stateFour", stateFour);

		dh_proxy = p_proxy;
		p_proxy->success = true;

        addTransferRule((uint32_t)State::initial, AppMessage::message_type::RESPONSE, (uint32_t)RequestEnum::delete_host,
                        rule_type::Result::success, boost::bind(&DeleteHost::on_step_one, this, _1, _2), (uint32_t)State::stateOne);

        addTransferRule((uint32_t)State::stateOne, AppMessage::message_type::REQUEST, (uint32_t)RequestEnum::query_host,
                        rule_type::Result::success, boost::bind(&DeleteHost::on_step_two, this, _1, _2), (uint32_t)State::stateTwo);

        addTransferRule((uint32_t)State::stateTwo, AppMessage::message_type::RESPONSE, (uint32_t)RequestEnum::query_host,
        		        rule_type::Result::any, boost::bind(&DeleteHost::on_step_three, this, _1, _2), (uint32_t)State::stateThree);

        addTransferRule((uint32_t)State::stateThree, AppMessage::message_type::RESPONSE, (uint32_t)EventEnum::timeout,
        		        rule_type::Result::any, boost::bind(&DeleteHost::on_timeout, this, _1, _2), (uint32_t)State::stateFour);
    }
    virtual void invokeSession(session_type& session) override{

		current_state = (uint32_t)State::initial;

        /*BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]recv delete request")
                     %session.getSessionID();
        setLoopTimer(session, 5);
        session.step_num = 0;
        BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]new timer id %d")
                     %session.getSessionID() %session.getTimerID();*/
    }

    void on_step_one(AppMessage& event, session_type& session){
		try{
	    	//current_state++;
			if ((uint32_t)State::initial != session.getCurrentState())
			{
				dh_proxy->success = false;
                throw std::logic_error("current state err on state one");
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]DeleteHost one, current state %d, event id %d")
						 %session.getSessionID() %session.getCurrentState() %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "DeleteHost task exception:" << ex.what();
		}

    }
    void on_step_two(AppMessage& event, session_type& session){

		try{
	    	//current_state++;
			if ((uint32_t)State::stateOne!= session.getCurrentState())
			{
				dh_proxy->success = false;
                throw std::logic_error("current state err on state two");
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]DeleteHost two, current state %d, event id %d")
						 %session.getSessionID() %session.getCurrentState() %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "DeleteHost task exception:" << ex.what();
		}

    }
    void on_step_three(AppMessage& event, session_type& session){

		try{
	    	//current_state++;
			if ((uint32_t)State::stateTwo!= session.getCurrentState())
			{
				dh_proxy->success = false;
                throw std::logic_error("current state err on state three");
			}
			BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]DeleteHost three, current state %d, event id %d")
						 %session.getSessionID() %session.getCurrentState() %event.id ;
		}
		catch(exception& ex){
			BOOST_LOG_TRIVIAL(error) << "DeleteHost task exception:" << ex.what();
		}

    }

    void on_timeout(AppMessage& event, session_type& session){
		session.step_num++;
        /*BOOST_LOG_TRIVIAL(info) << boost::format("[%08X]on_timeout, stepnum %d, event id %d")
                     %session.getSessionID() %session.step_num %event.id ;*/
    }

private:
	uint32_t current_state;

};

typedef BaseManager< T > task_manager_type;

class TaskManager:public BaseManager< BaseTask< session_type, Proxy > >{
public:
	bool success;
    TaskManager(Proxy* p_proxy):task_manager_type(my_max_session, my_thread_count){
        addTask(new CreateHost(p_proxy));
        //addTask(new CreateHost(p_proxy));
        addTask(new DeleteHost(p_proxy));

		success = true;
    }

	void ManagerTaskAdd(Proxy* p_proxy)
	{
	    addTask(new CreateHost(p_proxy));
	    return;
	}

};

BaseManagerTest::BaseManagerTest()
{
    //ctor
}

BaseManagerTest::~BaseManagerTest()
{
    //dtor
}

void BaseManagerTest::test_add_same_task(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

	task_manager.ManagerTaskAdd(&proxy);
}

bool BaseManagerTest::test(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type session_id;
    {
        AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::create_host);
		for (int i = 0; i < my_max_session; i++)
		{
            if(!task_manager.startTransaction(TaskType::create_host, msg, session_id))
            {
                BOOST_LOG_TRIVIAL(warning) << "BaseManagerTest test startTransaction "<< i <<" failed";
                return false;
            }
		}
    }
    {
        session_type::session_id_type delete_session;
        {
            AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::delete_host);
            task_manager.startTransaction(TaskType::delete_host, msg, delete_session);
        }

    	this_thread::sleep_for(chrono::milliseconds(450));
        {
            AppMessage msg(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
            msg.success = true;
            task_manager.processMessage(delete_session, msg);
        }

    	this_thread::sleep_for(chrono::milliseconds(450));
        {
            AppMessage msg(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
            msg.success = true;
            task_manager.processMessage(delete_session, msg);
        }
    }
    {
        if(task_manager.containsTransaction(session_id)){
            AppMessage msg(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
            msg.success = true;
            if(!task_manager.processMessage(session_id, msg)){
                BOOST_LOG_TRIVIAL(warning) << "process message fail";
            }
        }
    }
    this_thread::sleep_for(chrono::seconds(2));
//    task_manager.terminateTransaction(session_id);

    task_manager.stop();
    BOOST_LOG_TRIVIAL(info) << "BaseManagerTest test pass";
    return true;
}

bool BaseManagerTest::test_allocTrans(){

    return true;
}

bool BaseManagerTest::test_terminateTrans()
{
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type session_id;
	{
        bool allcResult = true;
        int idx = 1;
        while(true == allcResult)
        {
			AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::create_host);
			if(!task_manager.startTransaction(TaskType::create_host, msg, session_id)){
                allcResult = false;
				BOOST_LOG_TRIVIAL(info) << "test_terminateTrans start task fail";
				idx++;
				return false;
			}

        }

		idx = 5;

		this_thread::sleep_for(chrono::seconds(10));
		while(idx)
		{
		    task_manager.terminateTransaction(idx);

			idx--;
		}
		task_manager.terminateTransaction(5);
		task_manager.terminateTransaction(15);
	}

    this_thread::sleep_for(chrono::seconds(10));
    task_manager.stop();

	return false;
}


bool BaseManagerTest::test_startTrans()
{
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type session_id;
	{
		for (int i = 0; i < 5; i++)
		{
            AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::create_host);
			if(!task_manager.startTransaction(TaskType::create_host, msg, session_id))
			{
				BOOST_LOG_TRIVIAL(warning) << "BaseManagerTest test_startTrans startTransaction "<< i <<" failed";
				return false;
			}

		}
	}

    this_thread::sleep_for(chrono::seconds(10));
    task_manager.stop();

	return true;
}


bool BaseManagerTest::test_processMessage()
{
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type session_id;
	{
		for (int i = 0; i < 5; i++)
		{
            AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::create_host);
			if(!task_manager.startTransaction(TaskType::create_host, msg, session_id))
			{
				BOOST_LOG_TRIVIAL(warning) << "BaseManagerTest test_processMessage startTransaction "<< i <<" failed";
				return false;
			}


			AppMessage msg1(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
			msg1.success = true;
			task_manager.processMessage(session_id, msg1);
			task_manager.processMessage(session_id, msg1);
		}

		AppMessage msg2(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
		msg2.success = true;
		task_manager.processMessage(7, msg2);

	}

    this_thread::sleep_for(chrono::seconds(10));
    task_manager.stop();

	return true;
}



void BaseManagerTest::test_recombination1()
{

	return;
}



void BaseManagerTest::test_recombination2()
{
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type session_id;
    AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::create_host);
	if(!task_manager.startTransaction(TaskType::create_host, msg, session_id))
	{
		BOOST_LOG_TRIVIAL(info)<<"wangli test allocTransaction failed";
		return;
	}

	this_thread::sleep_for(chrono::milliseconds(450));

	task_manager.terminateTransaction(session_id);

    this_thread::sleep_for(chrono::seconds(4));
    task_manager.stop();

	return;
}


void BaseManagerTest::test_recombination3()
{
	return;
}


void BaseManagerTest::test_recombination4()
{
	return;
}


void BaseManagerTest::test_recombination5()
{
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

    session_type::session_id_type create_session;
	AppMessage msg_create1(AppMessage::message_type::REQUEST, RequestEnum::create_host);
	AppMessage msg_create2(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
	AppMessage msg_create3(AppMessage::message_type::EVENT, RequestEnum::join_domain);
	AppMessage msg_create4(AppMessage::message_type::EVENT, EventEnum::timeout);




	task_manager.startTransaction(TaskType::create_host, msg_create1, create_session);
	task_manager.processMessage(create_session, msg_create2);
	task_manager.processMessage(create_session, msg_create3);
	task_manager.processMessage(create_session, msg_create4);

    this_thread::sleep_for(chrono::seconds(4));
    task_manager.stop();

	return;
}


void BaseManagerTest::test_recombination6(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

	session_type::session_id_type delete_session;

	int idx = 0;
	while(idx < 5)
	{
		//session_type::session_id_type delete_session;
		{
			AppMessage msg(AppMessage::message_type::REQUEST, RequestEnum::delete_host);
			task_manager.startTransaction(TaskType::delete_host, msg, delete_session);
		}

		//this_thread::sleep_for(chrono::milliseconds(450));
		{
			AppMessage msg(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
			msg.success = true;
			task_manager.processMessage(delete_session, msg);
		}

		//this_thread::sleep_for(chrono::milliseconds(450));
		{
			AppMessage msg(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
			msg.success = true;
			task_manager.processMessage(delete_session, msg);
		}
		idx++;
	}
    this_thread::sleep_for(chrono::seconds(4));

    task_manager.stop();

    return;
}


void BaseManagerTest::test_recombination7(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

	session_type::session_id_type delete_session;

	int idx = 0;
	while(idx < my_max_session)
	{
		//session_type::session_id_type delete_session;
		AppMessage msg1(AppMessage::message_type::REQUEST, RequestEnum::delete_host);
		//task_manager.startTransaction(delete_session, msg1);

		AppMessage msg2(AppMessage::message_type::RESPONSE, RequestEnum::delete_host);
		msg2.success = true;
		//task_manager.processMessage(delete_session, msg2);

		AppMessage msg3(AppMessage::message_type::RESPONSE, EventEnum::timeout);
		msg3.success = true;

		task_manager.startTransaction(TaskType::delete_host, msg1, delete_session);
		task_manager.processMessage(delete_session, msg2);
		task_manager.processMessage(delete_session, msg3);

		idx++;
	}

    this_thread::sleep_for(chrono::seconds(4));

    task_manager.stop();

    return;
}

void BaseManagerTest::test_recombination8(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

	session_type::session_id_type delete_session;

	int idx = 0;
	int index = 0;
	for (index = 0; index < 5; index++)
	{
		BOOST_LOG_TRIVIAL(info)<<"test_recombination8 "<<index;
		while(idx < my_max_session)
		{
			AppMessage msg1(AppMessage::message_type::REQUEST, RequestEnum::delete_host);

			AppMessage msg2(AppMessage::message_type::RESPONSE, RequestEnum::delete_host);
			msg2.success = true;

			AppMessage msg3(AppMessage::message_type::RESPONSE, EventEnum::timeout);
			msg3.success = true;

			task_manager.startTransaction(TaskType::delete_host, msg1, delete_session);
			task_manager.processMessage(delete_session, msg2);
			task_manager.processMessage(delete_session, msg3);

			idx++;
		}

		this_thread::sleep_for(chrono::seconds(4));
		idx = 0;
	}

	this_thread::sleep_for(chrono::seconds(14));

    task_manager.stop();

    return;
}


bool BaseManagerTest::test_recombination9(){
    Proxy proxy;
    TaskManager task_manager(&proxy);

    task_manager.start();

	session_type::session_id_type create_session;
	session_type::session_id_type delete_session;

	int idx = 0;
	int index = 0;
	bool result = true;
	for (index = 0; index < 1; index++)
	{
		boost::uniform_int<> real(1, 999);

		while(idx < my_max_session)
		{
			boost::uniform_int<> real(1, 999);
			if ((real(gen)%2))
			{
				AppMessage msg1(AppMessage::message_type::REQUEST, RequestEnum::delete_host);

				AppMessage msg2(AppMessage::message_type::RESPONSE, RequestEnum::delete_host);
				msg2.success = true;

				AppMessage msg3(AppMessage::message_type::REQUEST, RequestEnum::query_host);
				msg2.success = true;

				AppMessage msg4(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
				msg2.success = true;

				AppMessage msg5(AppMessage::message_type::RESPONSE, EventEnum::timeout);
				msg3.success = true;

				task_manager.startTransaction(TaskType::delete_host, msg1, delete_session);
				task_manager.processMessage(delete_session, msg2);
				task_manager.processMessage(delete_session, msg3);
				task_manager.processMessage(delete_session, msg4);

			}
			else
			{
				AppMessage msg_create1(AppMessage::message_type::REQUEST, RequestEnum::create_host);
				AppMessage msg_create2(AppMessage::message_type::RESPONSE, RequestEnum::query_host);
				AppMessage msg_create3(AppMessage::message_type::EVENT, RequestEnum::join_domain);
				//AppMessage msg_create4(AppMessage::message_type::EVENT, EventEnum::timeout);


				task_manager.startTransaction(TaskType::create_host, msg_create1, create_session);
				task_manager.processMessage(create_session, msg_create2);
				//task_manager.processMessage(create_session, msg_create3);
				//task_manager.processMessage(create_session, msg_create4);


			}
			idx++;
		}

		//this_thread::sleep_for(chrono::seconds(4));
		idx = 0;
	}

	this_thread::sleep_for(chrono::seconds(14));
	if (!proxy.success)
	{
		BOOST_LOG_TRIVIAL(info)<<"base manager test fail";
		result = false;
	}

    task_manager.stop();

    return result;
}





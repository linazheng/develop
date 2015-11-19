#include <boost/log/trivial.hpp>
#include <thread>
#include <unistd.h>
#include <functional>
#include "service/message_queue_test.h"



MessageQueueTest::MessageQueueTest(const int &num) : num(num), counter(0), counter1(0) {
    msgQueue.bindHandler(std::bind(&MessageQueueTest::eventHandle, this, std::placeholders::_1));
    msgQueue.bindHandler(std::bind(&MessageQueueTest::eventHandle1, this, std::placeholders::_1));
    msgQueue.start();
    for(int i = 0; i< num; i++) {
        msg.push_back(i);
    }
}
void MessageQueueTest::eventHandle(msgType::queue_type queueList) {
    counter += queueList.size();

    //BOOST_LOG_TRIVIAL(info) <<  "msg----------------- " <<  queueList.size();
}
void MessageQueueTest::eventHandle1(msgType::queue_type queueList) {
    counter1 += queueList.size();

    //BOOST_LOG_TRIVIAL(info) <<  "msg++++++ " <<  queueList.size();
}
MessageQueueTest::~MessageQueueTest() {
    msgQueue.stop();
}
void MessageQueueTest::testInsertMsg() {
    msgQueue.insertMessage(0);
}
void MessageQueueTest::testPutMsg() {
    msgQueue.putMessage(1);
}
void MessageQueueTest::testPutMsgList() {
    msgQueue.putMessage(msg);
}
bool MessageQueueTest::test() {
    std::thread insert(&MessageQueueTest::testInsertMsg, this);
    std::thread put(&MessageQueueTest::testPutMsg, this);
    std::thread putList(&MessageQueueTest::testPutMsgList, this);

    insert.join();
    put.join();
    putList.join();
    BOOST_LOG_TRIVIAL(info)  << "counter: " << counter;
    return (counter == counter1) && (counter == num + 2);
}



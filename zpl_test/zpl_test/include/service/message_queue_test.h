#ifndef MESSAGE_QUEUE_TEST_H_INCLUDED
#define MESSAGE_QUEUE_TEST_H_INCLUDED

#include <service/message_queue.hpp>
#include <list>


class MessageQueueTest{
    public:
        typedef zhicloud::service::MessageQueue<int> msgType;
        MessageQueueTest(const int &num) ;
        void eventHandle(msgType::queue_type queueList);
        void eventHandle1(msgType::queue_type queueList);
        ~MessageQueueTest();
        void testInsertMsg();
        void testPutMsg();
        void testPutMsgList();
        bool test();
    private:
        zhicloud::service::MessageQueue<int>  msgQueue;
        std::list<int>  msg;
        int num;
        int counter;
        int counter1;
};

#endif // MESSAGE_QUEUE_TEST_H_INCLUDED

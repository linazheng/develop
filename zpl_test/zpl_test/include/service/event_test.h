#ifndef EVENT_TEST_H_INCLUDED
#define EVENT_TEST_H_INCLUDED

#include <service/event.hpp>
class  EventTest{
    public:
        EventTest(const int &loop_num);
        ~EventTest();

        void tester1();
        void tester2();
        bool test();
    private:
       zhicloud::service::Event  event1;
       zhicloud::service::Event event2;

       int num;
       int count1;
       int count2;

};


#endif // EVENT_TEST_H_INCLUDED

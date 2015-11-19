#ifndef TIMED_INVOKER_TEST_H_INCLUDED
#define TIMED_INVOKER_TEST_H_INCLUDED


#include <service/timed_invoker.h>


class TimedInvokerTest{
    public:
        TimedInvokerTest(const int &num);
        ~TimedInvokerTest();
        void handler();
        void handler1();

        bool test();
    private:
        int num;
        int count;
        int count1;

};


#endif // TIMED_INVOKER_TEST_H_INCLUDED

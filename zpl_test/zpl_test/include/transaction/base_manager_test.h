#ifndef BASEMANAGERTEST_H
#define BASEMANAGERTEST_H


class BaseManagerTest
{
    public:
        BaseManagerTest();
        virtual ~BaseManagerTest();
        bool test();
		void test_add_same_task();
		bool test_allocTrans();
		bool test_terminateTrans();
		bool test_startTrans();
		bool test_processMessage();
		void test_recombination1();
		void test_recombination2();
		void test_recombination3();
		void test_recombination4();
		void test_recombination5();
		void test_recombination6();
		void test_recombination7();
		void test_recombination8();
		bool test_recombination9();

    protected:
    private:

};

#endif // BASEMANAGERTEST_H
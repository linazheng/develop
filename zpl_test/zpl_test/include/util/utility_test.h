#ifndef UTILITYTEST_H
#define UTILITYTEST_H

#include "digest_test.h"
#include "domain_utility_test.h"
#include "generator_test.h"
#include "logging_test.h"
#include "serial_test.h"

using namespace zhicloud::util;

class UtilityTest
{
    public:
        UtilityTest();
        virtual ~UtilityTest();
        bool test();
		
    protected:
    private:
		
};

#endif // UTILITYTEST_H
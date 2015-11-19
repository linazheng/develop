#ifndef DIGESTTEST_H
#define DIGESTTEST_H

#include <util/digest.h>

using namespace zhicloud::util;

class DigestTest
{
    public:
        bool test();
    protected:
    private:
		Digest digestObj;
		uint32_t uiCrc;		
};

#endif // DIGESTTEST_H

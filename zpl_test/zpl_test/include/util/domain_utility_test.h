#ifndef DOMAINTEST_H
#define DOMAINTEST_H

#include <util/domain_utility.h>

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp>

using namespace zhicloud::util;
using namespace std;
using boost::asio::ip::udp;

class DomainUtilTest
{
    public:
        DomainUtilTest(const string&, const string& , const uint16_t& );
        virtual ~DomainUtilTest();
        bool DomainCliTest();
        bool DomainSrvTest();
    protected:
    private:
		DomainUtility DomainUtil;
		int tmp;
		
};

void DomainBindTest(const string&, const string&, const uint16_t&, const string&);


#endif // DOMAINTEST_H

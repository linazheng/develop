#ifndef TESTTRANSPORTER_H
#define TESTTRANSPORTER_H

#include <string>

using namespace std;

class TransporterTest{
public:
    TransporterTest(const string& ip);
    ~TransporterTest();
    bool test();
private:
	string IPv4;

};




#endif // TESTTRANSPORTER_H

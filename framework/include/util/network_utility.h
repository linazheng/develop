#ifndef NETWORKUTILITY_H
#define NETWORKUTILITY_H
#include <string>
#include <list>
using namespace std;
namespace zhicloud{
    namespace util{
        bool getMacAddress(list< string>& output, bool formated = false);
        //output:00:16:3E:XX:XX:XX
        string generateMAC(bool lower = false);
    }
}


#endif // NETWORKUTILITY_H

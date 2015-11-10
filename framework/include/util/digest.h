#ifndef DIGEST_H
#define DIGEST_H

#include <string>

using namespace std;
namespace zhicloud{
    namespace util{
        class Digest
        {
            public:
                static uint32_t crc32(const string& input);
                static string sha1_hex(const string& input);
                static string hex(const char* buf, const int& buf_length);
                static string hex(const string& input);
        };
    }

}



#endif // DIGEST_H

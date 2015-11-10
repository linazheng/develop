#ifndef MESSAGECACHE_H
#define MESSAGECACHE_H
#include <string>
#include <map>

using namespace std;

namespace zhicloud{
    namespace transport{
        class MessageCache
        {
            public:
                typedef uint32_t index_type;
                MessageCache(const index_type& count = 0, const index_type& index = 0, const string& data = "");
                virtual ~MessageCache();
                bool add(const index_type& index, const string& data);
                bool isFinished();
                string get();
                bool check();
                MessageCache(MessageCache&& other);
                MessageCache& operator=(MessageCache&& other);
            private:
                static const uint16_t max_timeout = 10;
                index_type _total;
                uint16_t _timeout;
                bool _finished;
                map< index_type, string > _cache;
        };

    }
}


#endif // MESSAGECACHE_H

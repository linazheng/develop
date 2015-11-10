#ifndef WHISPER_RECEIVER_H
#define WHISPER_RECEIVER_H

#include <string>
#include <list>
#include <sstream>
#include <fstream>
#include <set>
#include <map>
#include <vector>
#include <chrono>

using std::string;
using std::list;
using std::stringstream;
using std::ofstream;

namespace zhicloud{
    namespace transport{
        class WhisperReceiver
        {
            public:
                WhisperReceiver();
                virtual ~WhisperReceiver();
                void reset();
                void initial(const string& filename, const uint64_t& filesize, const uint32_t& block_size, const uint32_t& strip_length);
                void writeData(const uint64_t& strip_id, const uint64_t& block_id, const string& data);
                bool isFinished() const;
                void statistic(uint64_t& processed, uint64_t& total,  uint64_t& speed);
            private:
                class CachedStrip{
                public:
                    CachedStrip(const uint64_t& strip_id, const uint64_t& file_size, const uint32_t& block_size, const uint32_t& strip_length);
                    ~CachedStrip();
                    CachedStrip(CachedStrip&& other);
                    void writeBlock(const uint64_t& block_id, const string& data);
                    const uint64_t& position() const;
                    string data() const;
                    const bool& isFinished() const;
                private:
                    CachedStrip(const CachedStrip& other);
                    CachedStrip& operator=(const CachedStrip& other);
                    CachedStrip& operator=(CachedStrip&& other);
                private:
                    uint64_t _position;
                    bool _finished;
                    uint32_t _block_size;
                    uint32_t _strip_length;
                    uint32_t _block_count;
                    uint64_t _buffer_size;
                    stringstream _buffer;
                    std::vector< bool > _flag_vector;
                };

                uint64_t _file_size;
                uint32_t _block_size;
                uint32_t _strip_length;
                bool _finished;
                uint64_t _processed;
                uint64_t _last_processed;
                std::chrono::time_point< std::chrono::high_resolution_clock > _last_timepoint;
                ofstream _writer;
                std::map< uint64_t, CachedStrip > _cached_strip;
                std::set< uint64_t > _pending_strip;
        };

    }

}

#endif // WHISPER_RECEIVER_H

#ifndef WHISPER_SENDER_H
#define WHISPER_SENDER_H

#include <string>
#include <list>
#include <vector>
#include <map>
#include <set>
#include <functional>
#include <chrono>
#include <fstream>

using std::string;
using std::list;
using std::vector;
using std::map;
using std::set;

namespace zhicloud{
    namespace transport{
        class WhisperSender
        {
            public:
                class DataBlock{
                    public:
                        DataBlock(const string& data, const uint64_t& strip_id, const uint64_t& block_id);
                        ~DataBlock();
                        const string& data() const;
                        const uint64_t& strip_id() const;
                        const uint64_t& block_id() const;
                        DataBlock(DataBlock&& other);
                    private:
                        string _data;
                        uint64_t _strip_id;
                        uint64_t _block_id;
                };
                WhisperSender();
                virtual ~WhisperSender();
                void reset();
                void initial(const string& filename, const uint32_t& block_size, const uint32_t& strip_length, const uint32_t& cache_count);
                void complete(const uint64_t& strip_id, const uint64_t& block_id);
                bool isFinished() const;
                void fetchData(const size_t& max_process, list< DataBlock >& block_list);
                void fetchFailedData(const uint32_t& cache_index, list< DataBlock >& block_list);
                //@timeout_cache:set of cache index of timeout
                //throw logic_error when check fail
                void check(set< uint32_t >& timeout_cache);
                void statistic(uint64_t& processed, uint64_t& total, uint64_t& speed);
            private:
                void loadStripToCache(const uint32_t& cache_offset);
            private:
                enum class BlockStatus:uint16_t{
                    idle = 0,
                    process = 1,
                    finish = 2,
                    fail = 3,
                };
                class CachedBlock{
                public:
                    CachedBlock(string&& data, const uint64_t& strip_id, const uint64_t& block_id, const size_t& timeout);
                    ~CachedBlock();
                    CachedBlock(CachedBlock&& other);
                    const uint64_t& strip_id() const{
                        return _strip_id;
                    }
                    const uint64_t& block_id() const{
                        return _block_id;
                    }
                    const string& data() const{
                        return _data;
                    }
                    const BlockStatus& status() const{
                        return _status;
                    }
                    void status(const BlockStatus& value){
                        _status = value;
                    }
                    uint32_t& counter(){
                        return _counter;
                    }
                    uint32_t& max_counter(){
                        return _max_counter;
                    }
                    uint32_t& retry(){
                        return _retry;
                    }
                private:
                    string _data;
                    uint64_t _strip_id;
                    uint64_t _block_id;
                    uint32_t _counter;
                    uint32_t _max_counter;
                    uint32_t _retry;
                    BlockStatus _status;
                };
                const static uint32_t min_timeout;
                const static uint32_t max_timeout;
                const static uint32_t max_retry;
                const static uint32_t buffer_size;
                uint64_t _file_size;
                uint32_t _block_size;
                uint32_t _strip_length;
                vector< uint16_t > _data_ports;
                vector< vector < CachedBlock > > _cached_data;
                //key = strip id, value = cached offset
                map< uint64_t, uint32_t > _cached_strip;
                //from great to less
                vector< uint64_t > _strip_array;
                bool _finished;
                uint32_t _cache_count;
                uint32_t _cache_pos;
                uint64_t _processed;
                uint64_t _last_processed;
                std::chrono::time_point< std::chrono::high_resolution_clock > _last_timepoint;
                std::ifstream _reader;
                uint32_t _block_in_transport;
        };

    }

}


#endif // WHISPER_SENDER_H

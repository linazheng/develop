#ifndef SERIALIZE_H
#define SERIALIZE_H

#include <istream>
#include <vector>

using namespace std;

namespace zhicloud{
    namespace util{
        class Serialize{
            //all in network/big-endian
        public:
            typedef uint32_t ulong_type;
            typedef uint16_t ushort_type;
            static bool writeVariant(ostream& stream, const uint64_t& value);
            static bool writeString(ostream& stream, const char* buf, const size_t& buf_size);
            static bool writeString(ostream& stream, const string& content);
            static bool writeFloat(ostream& stream, const float& value);
            //2-bytes
            static bool writeShort(ostream& stream, const ushort_type& value);
            //4-bytes
            static bool writeLong(ostream& stream, const ulong_type& value);
            static bool writeStringArray(ostream& stream, const vector< string >& value);
            static bool writeVariantArray(ostream& stream, const vector< uint64_t >& value);

            static bool readVariant(istream& stream, uint64_t& output);
            static bool readVariant(istream& stream, uint32_t& output);
            static bool readString(istream& stream, string& output);
            static bool readFloat(istream& stream, float& output);
            //2-bytes
            static bool readShort(istream& stream, ushort_type& output);
            //4-bytes
            static bool readLong(istream& stream, ulong_type& output);
            static uint32_t zigzagEncode(const int32_t& input);
            static int32_t zigzagDecode(const uint32_t& input);
            static uint64_t zigzagEncode(const int64_t& input);
            static int64_t zigzagDecode(const uint64_t& input);
        };
    }
}
#endif // SERIALIZE_H

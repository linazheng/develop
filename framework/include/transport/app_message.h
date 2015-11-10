#ifndef APPMESSAGE_H
#define APPMESSAGE_H
#include <map>
#include <string>
#include <istream>
#include <vector>
#include <exception>
#include <util/define.hpp>

using namespace std;

namespace zhicloud{
    namespace transport{

        class AppMessage
        {
            //function
            public:
                typedef zhicloud::util::RequestEnum request_id_type;
                typedef zhicloud::util::EventEnum event_id_type;
                typedef zhicloud::util::ParamEnum key_type;
                typedef uint32_t message_id_type;
                //64bit
                typedef uint64_t uint_type;
                typedef vector<uint_type> uint_array_type;
                typedef vector<float> float_array_type;
                typedef vector<string> string_array_type;
                typedef vector<vector<uint_type>> uint_array_array_type;
                typedef vector<vector<float>> float_array_array_type;
                typedef vector<vector<string>> string_array_array_type;
                enum class message_type: uint32_t
                {
                    REQUEST = 0,
                    RESPONSE = 1,
                    EVENT = 2,
                    ACK = 3
                };
                explicit AppMessage(const message_type& type, const request_id_type& request_id);
                explicit AppMessage(const message_type& type, const event_id_type& event_id);
                explicit AppMessage();
                virtual ~AppMessage();
                void toString(string& output);
                void fromString(const string& content);
                //seter&getter
                bool setInt(const key_type& key, const int& value);
                bool setUInt(const key_type& key, const uint_type& value);
                bool setBoolean(const key_type& key, const bool& value);
                bool setFloat(const key_type& key, const float& value);
                bool setString(const key_type& key, const string& value);

                bool getInt(const key_type& key, int32_t& value);
                bool getUInt(const key_type& key, uint32_t& value);
                bool getUInt(const key_type& key, uint_type& value);
                bool getBoolean(const key_type& key, bool& value);
                bool getFloat(const key_type& key, float& value);
                bool getString(const key_type& key, string& value);

                int getInt(const key_type& key);
                uint_type getUInt(const key_type& key);
                bool getBoolean(const key_type& key);
                float getFloat(const key_type& key);
                string getString(const key_type& key);

                bool setUIntArray(const key_type& key, const uint_array_type& input);
                bool setFloatArray(const key_type& key, const float_array_type& input);
                bool setStringArray(const key_type& key, const string_array_type& input);

                bool getUIntArray(const key_type& key, uint_array_type& value);
                bool getFloatArray(const key_type& key, float_array_type& value);
                bool getStringArray(const key_type& key, string_array_type& value);

                uint_array_type getUIntArray(const key_type& key);
                float_array_type getFloatArray(const key_type& key);
                string_array_type getStringArray(const key_type& key);

                bool setUIntArrayArray(const key_type& key, const uint_array_array_type& input);
                bool setFloatArrayArray(const key_type& key, const float_array_array_type& input);
                bool setStringArrayArray(const key_type& key, const string_array_array_type& input);

                bool getUIntArrayArray(const key_type& key, uint_array_array_type& value);
                bool getFloatArrayArray(const key_type& key, float_array_array_type& value);
                bool getStringArrayArray(const key_type& key, string_array_array_type& value);

                uint_array_array_type getUIntArrayArray(const key_type& key);
                float_array_array_type getFloatArrayArray(const key_type& key);
                string_array_array_type getStringArrayArray(const key_type& key);

                explicit AppMessage(const AppMessage& other);
                explicit AppMessage(AppMessage&& other);
                AppMessage& operator=(const AppMessage& other);
                AppMessage& operator=(AppMessage&& other);
                bool containsKey(const key_type& key) const;
            protected:
            private:
                void writeParam(ostream& stream);
                void readParam(istream& stream);
                enum class param_type:uint32_t
                {
                    INT = 0,
                    UINT = 1,
                    BOOL = 2,
                    STRING = 3,
                    FLOAT = 4,
                    INT_ARRAY = 5,
                    UINT_ARRAY = 6,
                    FLOAT_ARRAY = 7,
                    STRING_ARRAY = 8,
                    UINT_ARRAY_ARRAY = 9,
                    STRING_ARRAY_ARRAY = 10,
                    FLOAT_ARRAY_ARRAY = 11
                };
            //member variable
            public:
                message_id_type id;
                message_type type;
                string sender;
                string receiver;
                uint32_t session;
                uint32_t sequence;
                uint32_t transaction;
                uint32_t timestamp;
                bool success;

            private:
                typedef uint32_t real_key_type;

                map< real_key_type, param_type> _key_map;

                map< real_key_type, int> _int_value;
                map< real_key_type, uint_type> _uint_value;
                map< real_key_type, bool> _bool_value;
                map< real_key_type, float> _float_value;
                map< real_key_type, string> _string_value;
                map< real_key_type, uint_array_type > _uint_array;
                map< real_key_type, float_array_type > _float_array;
                map< real_key_type, string_array_type > _string_array;
                map< real_key_type, uint_array_array_type > _uint_array_array;
                map< real_key_type, float_array_array_type > _float_array_array;
                map< real_key_type, string_array_array_type > _string_array_array;
        };
    }
}


#endif // APPMESSAGE_H

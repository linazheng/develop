#ifndef DATAGRAM_H
#define DATAGRAM_H
#include <string>
#include <list>
#include <exception>

using namespace std;

namespace zhicloud{
    namespace transport{
        class Datagram
        {
//            datagram format:
//            header(1 byte):
//              mark(4bit):1001
//              version(2bit):1~4
//              type(2bit):0-data, 1-ack
//            seq:2 byte
//            for data
//            length:2 byte
//            crc:4 byte - crc32
//            data:n byte
            public:
                Datagram(const unsigned short& sequence, const string& content = "", bool ack = false);
                virtual ~Datagram();
                string toString();
                static void fromString(const string& input, list<Datagram>& data_output, list<unsigned short>& ack_list);
                const uint16_t& seq() const;
                void seq(const uint16_t& value);
                const string& data() const;
                void data(const string& value);
                const bool& is_ack() const;
                void is_ack(const bool& value);
            private:
                static const unsigned char header_mask = 9;//bin:1001
                static const unsigned char verion = 1;//bin:01
                uint16_t _seq;
                string _data;
                bool _is_ack;

        };
    }
}

#endif // DATAGRAM_H

#ifndef COMMAND_H
#define COMMAND_H

#include <string>
#include <list>
#include <exception>

using namespace std;

namespace zhicloud{
    namespace transport{
        class Command{
        public:
                typedef uint32_t session_id_type;
                 enum class CommandType:uint16_t {
                    keep_alive = 0,
                    connect_request = 1,
                    connect_response = 2,
                    disconnect_request = 3,
                    disconnect_response = 4,
                    message_data = 5,
                    connect_acknowledge = 6
                };

                Command(const CommandType& type = CommandType::keep_alive);
                Command(const Command& other);
                Command(Command&& other);
                Command& operator=(const Command& other);
                Command& operator=(Command&& other);
                virtual ~Command();
                static void unpackageFromRawdata(const string& data, list<Command>& output);
                string toString() const;

                const session_id_type& session() const;
                void session(const session_id_type& id);
                const CommandType& type() const;
                void type(const CommandType& t);

                //ConnectRequest
                const string& client_key() const;
                void client_key(const string& key);
                const string& digest() const;
                void digest(const string& d);
                const session_id_type& sender() const;
                void sender(const session_id_type& id);
                const string& name() const;
                void name(const string& n);
                const string& ip() const;
                void ip(const string& value);
                const uint16_t& port() const;
                void port(const uint16_t& p);
                //ConnectResponse
                const bool& success() const;
                void success(const bool& value);
                const bool& need_digest() const;
                void need_digest(const bool& value);
                const uint16_t& auth_method() const;
                void auth_method(const uint16_t& value);
                const string& server_key() const;
                void server_key(const string& value);
                //MessageData
                const uint32_t& serial() const;
                void serial(const uint32_t& value);
                const uint32_t& index() const;
                void index(const uint32_t& value);
                const uint32_t& total() const;
                void total(const uint32_t& value);
                const string& data() const;
                void data(const string& value);

        private:
                void copy(const Command& other);
                void move_construct(Command&& other);
                string serializeConnectRequest() const;
                string serializeConnectResponse() const;
                string serializeConnectAcknowledge() const;
                string serializeDisconnectRequest() const;
                string serializeDisconnectResponse() const;
                string serializeKeepAlive() const;
                string serializeMessageData() const;

        private:
                session_id_type _session;
                CommandType _type;
                //ConnectRequest
                string _client_key;
                string _digest;
                session_id_type _sender;
                string _name;
                string _ip;
                uint16_t _port;
                //ConnectResponse
                bool _success;
                bool _need_digest;
                uint16_t _auth_method;
                string _server_key;
                //MessageData
                uint32_t _serial;
                uint32_t _index;
                uint32_t _total;
                string _data;
        };
    }
}


#endif // COMMAND_H

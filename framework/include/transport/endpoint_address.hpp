#ifndef ENDPOINT_ADDRESS_HPP_INCLUDED
#define ENDPOINT_ADDRESS_HPP_INCLUDED

#include <string>

using std::string;

namespace zhicloud{
    namespace transport{

        class EndpointAddress{
        public:
           EndpointAddress(const string& ip = "", const uint16_t& port = 0):_ip(ip), _port(port)
           {
           }
           ~EndpointAddress(){
           }
           EndpointAddress(const EndpointAddress& other){
                _ip = other._ip;
                _port = other._port;
            }
            EndpointAddress& operator=(const EndpointAddress& other){
                _ip = other._ip;
                _port = other._port;
                return *this;
            }
            EndpointAddress(EndpointAddress&& other){
                _ip = std::move(other._ip);
                _port = std::move(other._port);
            }
            EndpointAddress& operator=(EndpointAddress&& other){
                _ip = std::move(other._ip);
                _port = std::move(other._port);
                return *this;
            }
            const string& ip() const{
                return _ip;
            }
            void ip(const string& value){
                _ip = value;
            }
            const uint16_t& port() const{
                return _port;
            }
            void port(const uint16_t& value){
                _port = value;
            }
        private:
            string _ip;
            uint16_t _port;
        };
    }
}

#endif // ENDPOINT_ADDRESS_HPP_INCLUDED

#ifndef SERVER_STATUS_HPP
#define SERVER_STATUS_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class ServerStatus{
        public:
            ServerStatus()
            {
            }

            ServerStatus& operator=(const ServerStatus& other)
            {

                copy(other);
                return *this;
            }

            ServerStatus(const ServerStatus& other)
            {
                 copy(other);
            }            
            const string& getName()const { return _self.getName();}
            const string& getUUID()const { return _self.getUuid();}
            const string& getIp()const {return _ip;}
            const BaseCounter& getCounter()const { return _counter;}


            void setName(const string& value) {  _self.setName(value);}
            void setUUID(const string& value) {  _self.setUUID(value);}
            void setIp(const string& value) { _ip = value;}
            void SetCounter(const BaseCounter& value) {  _counter = value;}

        private:
            void copy(const ServerStatus& other)
            {
                _self = other._self;
                _counter = other._counter;
                _ip = other._ip;
            }

            BaseSelfInfo _self;
            BaseCounter _counter;
            string _ip;


        };

        class ServerRackStatus{
        public:
            ServerRackStatus()
            {
            }
            
            ServerRackStatus& operator=(const ServerRackStatus& other)
            {

                copy(other);
                return *this;
            }

            ServerRackStatus(const ServerRackStatus& other)
            {
                 copy(other);
            }            
            const string& getName()const { return _self.getName();}
            const string& getUUID()const { return _self.getUuid();}
            const BaseCounter& getCounter()const { return _counter;}
            const StatusCounter& getServerCounter()const { return _server;}

            void setName(const string& value) {  _self.setName(value);}
            void setUUID(const string& value) {  _self.setUUID(value);}
            void SetCounter(const BaseCounter& value) {  _counter = value;}
            void SetServerCounter(const StatusCounter& value) {  _server = value;}


         private:
            void copy(const ServerRackStatus& other)
            {
                _self = other._self;
                _counter = other._counter;
                _server = other._server;
            }

            BaseSelfInfo _self;
            BaseCounter _counter;
            StatusCounter _server;
        };

        class ServerRoomStatus{
        public:
            ServerRoomStatus()
            {
            }
            
            ServerRoomStatus& operator=(const ServerRoomStatus& other)
            {           
                copy(other);
                return *this;
            }
            
            ServerRoomStatus(const ServerRoomStatus& other)
            {
                copy(other);
            }           

            const string& getName()const { return _self.getName();}
            const string& getUUID()const { return _self.getUuid();}
            const BaseCounter& getCounter()const { return _counter;}
            const StatusCounter& getServerCounter()const { return _server;}

            void setName(const string& value) {  _self.setName(value);}
            void setUUID(const string& value) {  _self.setUUID(value);}
            void SetCounter(const BaseCounter& value) {  _counter = value;}
            void SetServerCounter(const StatusCounter& value) {  _server = value;}
        private:

            
            void copy(const ServerRoomStatus& other)
            {
                _self = other._self;
                _counter = other._counter;
                 _server = other._server;
            }

            BaseSelfInfo _self;
            BaseCounter _counter;
            StatusCounter _server;
        };
    }
}


#endif // SERVER_STATUS_HPP

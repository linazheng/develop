#ifndef SERVER_STATUS_HPP
#define SERVER_STATUS_HPP

#include "Util.hpp"
#include "Status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class ServerStatus{
        public:
            ServerStatus()
            {
            }
        private:
            BaseSelfInfo _self;
            BaseCounter _counter;
            string _ip;


        };

        class ServerRackStatus{
        public:
            ServerRackStatus()
            {
            }
         private:
            BaseSelfInfo _self;
            BaseCounter _counter;
            StatusCounter _server;
        };

        class ServerRoomStatus{
        public:
            ServerRoomStatus()
            {
            }
        private:
            BaseSelfInfo _self;
            BaseCounter _counter;
            StatusCounter _server;
        };
    }
}


#endif // SERVER_STATUS_HPP

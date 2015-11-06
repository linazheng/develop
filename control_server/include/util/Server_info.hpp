#ifndef SERVER_INFO_HPP
#define SERVER_INFO_HPP

#include "Util.hpp"

namespace zhicloud
{
    namespace control_server{

        class ServerInfo{
        public:
            ServerInfo()
            {
            }
        private:
            BaseSelfInfo _self;
            string _rack;
            string _ip;
        };

        class ServerRackInfo{
        public:
            ServerRackInfo()
            {
            }
        private:
            BaseSelfInfo _self;
            string _room;
        };

        class ServerRoomInfo{
        public:
            ServerRoomInfo()
            {
            }
        private:
            BaseSelfInfo _self;
            string _domain;
            string _display_name;
            string _description;
        };


    }
}


#endif // SERVER_INFO_HPP

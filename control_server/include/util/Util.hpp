#ifndef UTIL_HPP_INCLUDED
#define UTIL_HPP_INCLUDED

#include <string>
#include <map>
#include <set>
#include <vector>
#include <arpa/inet.h>
#include <mutex>
using namespace std;

namespace zhicloud
{
    namespace control_server{
        typedef string UUID_TYPE;

        enum class MonitorLevelEnum:uint32_t
        {
            system = 0,
            server_room = 1,
            server_rack = 2,
            server = 3,
            compute_node = 4,
            storage_node = 5,
            host = 6,
        };


        enum class OptionStatusEnum:uint32_t
        {
            disabled = 0,
            enabled = 1,
        };


        class BaseSelfInfo{
        public:
            BaseSelfInfo()
            {
            }

            BaseSelfInfo(const string& name,const string& uuid):_name(name),_uuid(uuid)
            {

            }

            const string& getName() const
            {
                return _name;
            }
            const UUID_TYPE& getUuid() const
            {
                return _uuid;
            }
        private:
            string _name;
            UUID_TYPE _uuid;

        };
    }
}

#endif // UTIL_HPP_INCLUDED

#ifndef EXPIREMANAGER_H
#define EXPIREMANAGER_H

#include <util/logging.h>
#include "util.hpp"

namespace zhicloud
{
    namespace control_server{

        class ExpireManager
        {
        public:
            ExpireManager(const string& logger_name);
            ~ExpireManager();

            bool start(const string& resource_name);
            bool updateFound(const string& resource_name, const set<UUID_TYPE>& id_list);
            bool updateLost(const string& resource_name, const set<UUID_TYPE>& id_list);
            bool isFound(const string& resource_name,const UUID_TYPE& uuid,const uint32_t & max_expire);
            bool isLost(const string& resource_name,const UUID_TYPE& uuid,const uint32_t & max_expire);

            bool finish(const string& resource_name);
        protected:
            ExpireManager(){}
            bool check(const string& resource_name,const UUID_TYPE& uuid,const uint32_t & max_expire);
            bool update(const string& target_name,const set<UUID_TYPE>& id_list);

        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            const static uint32_t _tresource_type_host;
            const static uint32_t _expire_type_found;
            const static uint32_t _expire_type_lost;

            map<string,map<UUID_TYPE,uint32_t>> _expire; //##key = name:[resource_type]_[resource_name]_[expire_type],etc: "0_ncxxx_1"##value = map<id, counter>
        };
}
}

#endif // EXPIREMANAGER_H

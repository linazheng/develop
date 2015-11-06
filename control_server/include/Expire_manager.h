#ifndef EXPIREMANAGER_H
#define EXPIREMANAGER_H

#include <util/logging.h>
#include "Util.hpp"

namespace zhicloud
{
    namespace control_server{

        enum class ExpireTypeEnum:uint32_t
        {
            expire_type_found = 0,
            expire_type_lost = 1,
        };


        class ExpireManager
        {
        public:
            ExpireManager(const string& logger_name);
            ~ExpireManager();

        protected:
            ExpireManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            const static uint32_t _tresource_type_host;

            map<string,map<UUID_TYPE,uint32_t>> _expire; //##key = name:[resource_type]_[resource_name]_[expire_type],etc: "0_ncxxx_1"##value = map<id, counter>
        };
}
}

#endif // EXPIREMANAGER_H

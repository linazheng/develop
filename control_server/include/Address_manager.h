#ifndef ADDRESSMANAGER_H
#define ADDRESSMANAGER_H


#include <util/logging.h>
#include "Address_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class AddressManager
        {
        public:
            AddressManager(const string& resource_path,const string& logger_name);
            ~AddressManager();

        protected:
            AddressManager(){}
        private:

            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            map<UUID_TYPE,AddressPool> _address_pool;
            bool _modified;
        };
    }
}

#endif // ADDRESSMANAGER_H

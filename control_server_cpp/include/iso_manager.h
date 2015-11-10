#ifndef ISOMANAGER_H
#define ISOMANAGER_H


#include <util/logging.h>
#include "iso_image.hpp"

namespace zhicloud
{
    namespace control_server{

        class ISOManager
        {
        public:
            ISOManager(const string& logger_name);
            ~ISOManager();

        protected:
            ISOManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            map<UUID_TYPE,ISOImage> _iso;
            map<string,UUID_TYPE> _iso_name;//key = image name, value = uuid
            map<string,vector<UUID_TYPE>> _iso_containers;//key = service name, value = list of image uuid
        };
    }
}

#endif // ISOMANAGER_H

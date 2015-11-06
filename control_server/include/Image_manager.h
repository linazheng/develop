#ifndef IMAGEMANAGER_H
#define IMAGEMANAGER_H

#include <util/logging.h>
#include "Disk_image.hpp"

namespace zhicloud
{
    namespace control_server{
    class ImageManager
    {
        public:
            ImageManager(const string& logger_name);
            ~ImageManager();

        protected:
            ImageManager(){}
        private:
            typedef unique_lock<recursive_mutex> lock_type;
            mutable recursive_mutex _mutex;
            util::logger_type _logger;

            map<UUID_TYPE,DiskImage> _images;
            map<string,UUID_TYPE> _images_name;//# #key = image name, value = uuid
            map<string,vector<UUID_TYPE>> _image_containers;//key = service name, value = list of image uuid

        };
    }
}

#endif // IMAGEMANAGER_H

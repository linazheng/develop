#include "Image_manager.h"


using namespace zhicloud;
using namespace control_server;
using namespace util;

ImageManager::ImageManager(const string& logger_name)
{
    _logger = getLogger(logger_name);
}

ImageManager::~ImageManager()
{
    //dtor
}

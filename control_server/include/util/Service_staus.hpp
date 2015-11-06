#ifndef SERVICE_STAUS_HPP
#define SERVICE_STAUS_HPP

#include "Util.hpp"
#include "Status_info.hpp"
#include "Compute_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class WhisperService{
        public:
            WhisperService():_type(0),_port(0)
            {
            }
        private:
            string _name;
            uint32_t _type;
            string _ip;
            uint32_t _port;
        };

        class ServiceStatus{
        public:
            ServiceStatus():_type(0),_port(0),_status(UnitStatusEnum::status_stop),_disk_type(ComputeStorageTypeEnum::local)
            {
            }

            bool isRunning()
            {
                return (_status == UnitStatusEnum::status_running);
            }

            bool isStopped()
            {
                return (_status == UnitStatusEnum::status_stop);
            }

        private:
            string _name;
            uint32_t _type;
            string _group;
            string _ip;
            uint32_t _port;
            UnitStatusEnum _status;
            string _version;
            string _server;
            ComputeStorageTypeEnum _disk_type;

        };
    }
}

#endif // SERVICE_STAUS_HPP

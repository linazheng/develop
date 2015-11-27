#ifndef SERVICE_STAUS_HPP
#define SERVICE_STAUS_HPP

#include "util.hpp"
#include "status_info.hpp"
#include "compute_pool.hpp"

namespace zhicloud
{
    namespace control_server{

        class WhisperService{
        public:
            WhisperService():_type(0),_port(0)
            {
            }

            WhisperService& operator=(const WhisperService& other)
            {

                copy(other);
                return *this;
            }

            WhisperService(const WhisperService& other)
            {
                 copy(other);
            }

            const string& getName()const {return _name;}
            const uint32_t& getType()const {return _type;}
            const string& getIp()const {return _ip;}
            const uint32_t& getPort()const {return _port;}

            void setName(const string& value) { _name = value;}
            void setType(const uint32_t& value) { _type = value;}
            void setIp(const string& value) { _ip = value;}
            void setPort(const uint32_t& value) { _port = value;}

        private:
            void copy(const WhisperService& other)
            {
                _name = other._name;
                _type = other._type;
                _ip = other._ip;
                _port = other._port;
            }

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

            ServiceStatus& operator=(const ServiceStatus& other)
            {

                copy(other);
                return *this;
            }

            ServiceStatus(const ServiceStatus& other)
            {
                 copy(other);
            }


            const string& getName()const {return _name;}
            const uint32_t& getType()const {return _type;}
            const string& getGroup()const {return _group;}
            const string& getIp()const {return _ip;}
            const uint32_t& getPort()const {return _port;}
            const string& getVersion()const {return _version;}
            const UUID_TYPE& getServer()const {return _server;}
            const UnitStatusEnum& getStatus()const {return _status;}
            const ComputeStorageTypeEnum& getDiskType()const {return _disk_type;}

            void setName(const string& value) { _name = value;}
            void setType(const uint32_t& value) { _type = value;}
            void setGroup(const string& value) { _group = value;}
            void setIp(const string& value) { _ip = value;}
            void setPort(const uint32_t& value) { _port = value;}
            void setVersion(const string& value) { _version = value;}
            void setServer(const UUID_TYPE& value) { _server = value;}
            void setStatus(const UnitStatusEnum& value) { _status = value;}
            void setDiskType(const ComputeStorageTypeEnum& value) { _disk_type = value;}

        private:
            void copy(const ServiceStatus& other)
            {
                _name = other._name;
                _type = other._type;
                _group = other._group;
                _ip = other._ip;
                _port = other._port;
                _status = other._status;
                _version = other._version;
                _server = other._server;
                _disk_type = other._disk_type;
            }

            string _name;
            uint32_t _type;
            string _group;
            string _ip;
            uint32_t _port;
            UnitStatusEnum _status;
            string _version;
            UUID_TYPE _server;
            ComputeStorageTypeEnum _disk_type;

        };
    }
}

#endif // SERVICE_STAUS_HPP

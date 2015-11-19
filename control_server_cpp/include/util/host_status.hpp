#ifndef HOST_STATUS_HPP
#define HOST_STATUS_HPP

#include "util.hpp"
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class HostIp
        {
        public:
            HostIp()
            {
            }

            const string& getTargetIp()const { return  _target_ip; }
            const string& getPublicIp()const { return _public_ip; }

            void setTargetIp(const string& value) { _target_ip = value; }
            void setPublicIp(const string& value) { _public_ip = value; }

        private:
            string _target_ip;
            string _public_ip;
        };
        class HostStatus{
        public:
            HostStatus():_memory_usage(0.0),_disk_usage(0.0)
            {

            }


            HostStatus& operator=(const HostStatus& other)
            {

                copy(other);
                return *this;
            }

            HostStatus(const HostStatus& other)
            {
                 copy(other);
            }

            const UUID_TYPE& getUUID()const { return  _uuid; }
            const UUID_TYPE& getServerUUID()const { return _server_uuid; }
            const HostIp& getHostIp()const { return _ip; }
            const float& getMemoryUsage() const { return _memory_usage;}
            const float& getDiskUsage() const { return _disk_usage;}
            const BaseCounter& getBaseCounter() const { return _counter;}

            void setUUID(const UUID_TYPE& value){ _uuid = value; }
            void setServerUUID(const UUID_TYPE& value) { _server_uuid = value; }
            void setHostIp(const HostIp& value) {  _ip = value; }
            void setMemoryUsage(const float& value) { _memory_usage = value;}
            void setDiskUsage(const float& value) { _disk_usage = value;}
            void setBaseCounter(const BaseCounter& value) {_counter = value;}

        private:

            void copy(const HostStatus& other)
            {
                _counter = other._counter;
                _memory_usage = other._memory_usage;
                _disk_usage = other._disk_usage;
                _server_uuid = other._server_uuid;
                _uuid = _uuid;
                _ip = other._ip;

            }

            BaseCounter _counter;
            float _memory_usage;
            float _disk_usage;
            UUID_TYPE _server_uuid;//##server uuid
            UUID_TYPE _uuid;
            HostIp _ip;//##[target_ip, public_ip]
        };
    }

}


#endif // HOST_STATUS_HPP

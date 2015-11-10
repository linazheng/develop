#ifndef ADDRESS_POOL_HPP
#define ADDRESS_POOL_HPP


#include "util.hpp"

namespace zhicloud
{
    namespace control_server{

        class AddressResource{
        public:
            AddressResource(const string& ip,const uint32_t& count):_ip(ip),_count(count),_last_offset(0),_modified(true),
                    _enable(OptionStatusEnum::enabled)
            {

                _begin = ntohl(inet_addr(_ip.c_str()));
                _end = _begin + _count;
            }

            void setModified(const bool& modified)
            {
                _modified = modified;
            }


            bool isModified()
            {
                return _modified;
            }

            size_t allocatedCount()
            {
                return _allocated_ip.size();
            }


        private:
            string _ip;
            uint32_t _count;
            uint32_t _begin;
            uint32_t _end;
            uint32_t _last_offset;
            bool _modified;
            OptionStatusEnum _enable;
            set<uint32_t> _allocated_ip;
        };

        class AddressPool{
        public:
            AddressPool():_modified(true),_enable(OptionStatusEnum::enabled)
            {

            }

            void setModified(const bool& modified)
            {
                _modified = modified;
            }


            bool isModified()
            {
                return _modified;
            }

        private:
            BaseSelfInfo _self;
            bool _modified;
            OptionStatusEnum _enable;

            map<uint32_t,AddressResource> _resource;// //key = start ip, value = AddressResource
        };
    }
}

#endif // ADDRESS_POOL_HPP

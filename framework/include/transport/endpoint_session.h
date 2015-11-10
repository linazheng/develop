#ifndef ENDPOINTSESSION_H
#define ENDPOINTSESSION_H

#include <string>
#include <map>
#include <mutex>
#include <transport/message_cache.h>
#include <transport/endpoint_address.hpp>

namespace zhicloud{
    namespace transport{
        class EndpointSession
        {
            public:
                typedef uint32_t session_id_type;
                typedef uint32_t serial_type;
                typedef uint32_t cache_index_type;
                typedef EndpointAddress address_type;
                EndpointSession(const session_id_type& session = 0, const serial_type& max_serial = 0xFFFF);
                EndpointSession(EndpointSession&& other);
                virtual ~EndpointSession();
                bool allocate(const string& remote_name);
                void deallocate();
                bool isConnected() const;
                void setConnected();
                void allocateSerial(session_id_type& serial);
                void store(const session_id_type& remote_session, address_type&& remote_address, address_type&& nat_address);
                void active(const string& remote_name);
                bool check();
                bool cacheData(const serial_type& serial, const cache_index_type& total, const cache_index_type& index, const string& data);
                string fetchCache(const serial_type& serial);
                const string& getRemoteName() const;
                void getRemoteSession(session_id_type& remote_session, address_type& nat_address);
                void getNatAddress(address_type& remote_address);
            private:
                void assureAllocated() const;
            private:
                typedef map< serial_type, MessageCache > cache_map_type;
                static const uint32_t max_timeout;
                session_id_type _session_id;
                bool _connected;
                bool _allocated;
                session_id_type _remote_session;
                string _remote_name;
                address_type _remote_address;
                address_type _nat_address;
                cache_map_type _cache_map;
                serial_type _last_serial;
                serial_type _max_serial;
                uint32_t _timeout;
                mutable std::mutex mutex;
                typedef std::lock_guard< std::mutex > lock_type;
        };
    }
}



#endif // ENDPOINTSESSION_H

#ifndef ENDPOINTMANAGER_H
#define ENDPOINTMANAGER_H

#include <string>
#include <map>
#include <list>
#include <mutex>
#include <transport/endpoint_address.hpp>
#include <transport/endpoint_session.h>
#include <util/copyable_atomic.hpp>

using zhicloud::util::CopyableAtomic;

namespace zhicloud{
    namespace transport{
        class EndpointManager
        {
            public:
                typedef EndpointSession::session_id_type session_id_type;
                typedef EndpointSession::serial_type serial_type;
                typedef EndpointAddress  address_type;
                EndpointManager(const session_id_type& max_capacity = 1024, const serial_type& max_serial = 0xFFFF);
                virtual ~EndpointManager();
                void allocate(const string& remote_name, session_id_type& output);
                void deallocate(const session_id_type& id);
                bool isAllocated(const string& remote_name, session_id_type& output);
                bool checkTimeout(list<session_id_type>& timeout_list);
                list<session_id_type> getAllConnected();

                //new interface
                void store(const session_id_type& id,  const session_id_type& remote_session, address_type&& remote_address, address_type&& nat_address);
                void getRemoteSession(const session_id_type& id, session_id_type& remote_session, address_type& nat_address);
                void getRemoteName(const session_id_type& id, string& remote_name);
                void getNatAddress(const session_id_type& id, address_type& remote_address);
                void active(const session_id_type& id, const string& remote_name);
                void setConnected(const session_id_type& id);
                void allocateSerial(const session_id_type& id, session_id_type& serial);
                //return:true = cache finished
                bool cacheData(const session_id_type& id, const session_id_type& serial, const uint32_t& total, const uint32_t& index, const string& data);
                string fetchCache(const session_id_type& id, const session_id_type& serial);
            private:
                void assureAllocated(const session_id_type& id);

            private:
                typedef map< session_id_type, EndpointSession > session_map_type;
                typedef map< session_id_type, CopyableAtomic< bool > > allocated_map_type;
                typedef map< string, session_id_type > name_map_type;
                session_map_type session_map;
                allocated_map_type allocated_map;
                name_map_type name_map;
                session_id_type last_id;
                session_id_type max_capacity;
                mutable std::mutex name_mutex;
                typedef std::lock_guard< std::mutex > lock_type;
        };
    }
}


#endif // ENDPOINTMANAGER_H

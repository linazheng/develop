#ifndef DOMAINUTILITY_H
#define DOMAINUTILITY_H

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp>
#include <service/runable.hpp>
#include <util/logging.h>

using namespace std;
using boost::asio::ip::udp;

namespace zhicloud{
    namespace util{
        class DomainUtility:public zhicloud::service::Runable
        {
            public:
                typedef boost::signals2::signal< void (const string&, const string&, const uint16_t&, const string&) > event_type;
                typedef event_type::slot_type event_handler;
                DomainUtility(const string& domain_name, const string& address = "224.6.6.6", const uint16_t& port = 5666);
                virtual ~DomainUtility();
                void bindHandler(const event_handler& handler);
                void addService(const string& service_name, const string& address, const uint16_t& port);
                bool publish();
                void query();
            protected:
                virtual bool onStart();
                virtual void onStopping();
                virtual void onWaitFinish();
                virtual void onStopped();

            private:
                DomainUtility(const DomainUtility& other);
                DomainUtility& operator=(const DomainUtility& other);
                void handleNotify(const string& service_name, const string& address, const uint16_t& port);
                void handleQuery(const uint16_t& request_id, const string& request_ip);
                void handleResponse(const string& service_name, const string& address, const uint16_t& port, const string& request_ip);
                void workingProcess();
                void handle_receive(const boost::system::error_code& error, std::size_t bytes_transferred);
                void handle_send(const boost::system::error_code& error, std::size_t bytes_transferred);
                void sendPacket(const string& data, const udp::endpoint& remote_address);
                void tryReceive();

                event_type onServiceAvailable;
                struct ServiceInfo{
                    string name;
                    string ip;
                    uint16_t port;
                };

                static const unsigned int bufsize = 512;

                char send_buffer[bufsize];
                char receive_buffer[bufsize];
                string group_ip;
                uint16_t group_port;
                bool published;
                uint16_t request_id;
                string domain_name;
                list< ServiceInfo > service_list;
                logger_type logger;
                boost::shared_ptr< boost::thread > work_thread;
                boost::asio::io_service io_service;
                std::unique_ptr< boost::asio::io_service::work > work;
                udp::socket socket;
                udp::endpoint remote_endpoint;
                udp::endpoint group_endpoint;
        };
    }
}


#endif // DOMAINUTILITY_H

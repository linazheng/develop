#ifndef WHISPER_H
#define WHISPER_H

#include <string>
#include <mutex>
#include <map>
#include <chrono>
#include <transport/endpoint_address.hpp>
#include <transport/packet_receiver.h>
#include <transport/packet_sender.h>
#include <transport/app_message.h>
#include <service/runable.hpp>
#include <service/timer_service.h>
#include <util/logging.h>
#include <util/generator.h>
#include <transport/whisper_task_manager.h>
#include <boost/signals2.hpp>

using std::string;
using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transport{
    class Whisper:public zhicloud::service::Runable
    {
        public:
            typedef EndpointAddress address_type;
            typedef WhisperSession::session_id_type task_id_type;
            typedef std::chrono::milliseconds duration_type;
            Whisper(const string& ip, const size_t& channel_count, const string& path, const size_t& work_thread = 2);
            virtual ~Whisper();
            const string& ip() const;
            void ip(const string& value);
            const uint16_t& control_port() const;
            template <class T >
            void bindObserver(T* observer){
                _on_start_event.connect(boost::bind(&T::onTaskStart, observer, _1, _2));
                _on_progress_event.connect(boost::bind(&T::onTaskProgress, observer, _1, _2, _3, _4, _5));
                _on_success_event.connect(boost::bind(&T::onTaskSuccess, observer, _1, _2, _3));
                _on_fail_event.connect(boost::bind(&T::onTaskFail, observer, _1, _2));
            }
            void attachFile(const string& filename, string& file_id);
            void detachFile(const string& file_id);
            bool containsFile(const string& file_id);
            void getFilename(const string& file_id, string& filename);
            void generateFile(string& file_id, string& filename);
            void fetchFile(const string& file_id, const string& target_file);
            void beginWrite(const string& local_file_id, const address_type& remote_address, task_id_type& task_id);
            void beginRead(const string& remote_file_id, const address_type& remote_address, task_id_type& task_id);
            void sendMessage(AppMessage& msg, const string& ip, const uint16_t& port);
            void onPacketReceived(const string& packet_data, const string& from_ip, const uint16_t& from_port,
                                                const string& to_ip, const uint16_t& to_port,  int socket_id);
            void getReceivePorts(vector< uint64_t >& ports);
            int32_t  setTimer(const duration_type& timeout, const task_id_type& task_id);
            int32_t  setLoopTimer(const duration_type& interval, const task_id_type& task_id);
            bool clearTimer(const int32_t& timer_id);
            constexpr static uint32_t getTimerInterval(){
                return 100;
            }
            void onTaskStart(const task_id_type& task_id, const uint16_t& task_type);
            void onTaskProgress(const task_id_type& task_id, const uint16_t& task_type, const uint64_t& current,
                                        const uint64_t& total, const uint64_t& speed);
            void onTaskSuccess(const task_id_type& task_id, const uint16_t& task_type, const string& file_id);
            void onTaskFail(const task_id_type& task_id, const uint16_t& task_type);

        protected:
            virtual bool onStart();
            virtual void onStopping();
        private:
            bool initial();
            void serializeToPacket(AppMessage& msg, string& packet_data);
            void unserializeFromPacket(const string& packet_data, AppMessage& msg);
            bool setNonBlocking(int socket);
            void onTimeoutEvent(list< AppMessage >& event_list);


        private:
            typedef std::lock_guard< std::recursive_mutex > lock_type;
            enum class CommandTypeEnum: uint64_t{
                write = 1,
                read = 2,
                data = 3,
                finish = 4,
                write_ack = 5,
                read_ack = 6,
                data_ack = 7,
                ready = 8,
                finish_ack = 9,
            };

            const static uint64_t max_session_count;
            const static uint16_t min_port;
            const static uint16_t max_port;
            string _ip;
            uint16_t _port;
            size_t _channel;
            string _file_path;
            std::recursive_mutex _file_mutex;
            //key=file id, value = filename
            map< string, string > _file_map;
            zhicloud::util::logger_type logger;
            zhicloud::util::Generator _generator;
            WhisperTaskManager _task_manager;
            PacketSender _sender;
            PacketReceiver _receiver;
            vector< int > _sockets;
            vector< uint64_t > _local_port;
            TimerService _timer_service;
            boost::signals2::signal< void (const uint32_t& , const uint16_t& ) > _on_start_event;
            boost::signals2::signal< void (const uint32_t& , const uint16_t&, const uint64_t&, const uint64_t&, const uint64_t& ) > _on_progress_event;
            boost::signals2::signal< void (const uint32_t& , const uint16_t&, const string& ) > _on_success_event;
            boost::signals2::signal< void (const uint32_t& , const uint16_t& ) > _on_fail_event;
            //key=task id, value = file id
            map< task_id_type, string > _task_file;
    };
}

}
#endif // WHISPER_H

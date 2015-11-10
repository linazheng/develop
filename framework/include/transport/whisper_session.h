#ifndef WHISPER_SESSION_H
#define WHISPER_SESSION_H

#include <string>
#include <mutex>
#include <transport/app_message.h>
#include <transport/whisper_sender.h>
#include <transport/whisper_receiver.h>

using std::string;
using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transport{
        class WhisperSession
        {
            public:
                typedef uint32_t session_id_type;
                typedef uint32_t state_type;
                typedef int32_t timer_id_type;
                enum class TaskTypeEnum:uint16_t{
                    invalid = 0,
                    read_receive = 1,
                    read_send = 2,
                    write_send = 3,
                    write_receive = 4,
                };
                const static int32_t invalid_timer_id;

                WhisperSession(const session_id_type& session_id = 0);
                virtual ~WhisperSession();
                void reset();
                bool occupy(const TaskTypeEnum& task_type);
                bool isInitialed() const;
                void initial(const AppMessage& msg);
                constexpr static state_type getInitialState(){
                    return 0;
                }
                constexpr static state_type getFinalState(){
                    return 0xFFFFFFFF;
                }
                bool isFinished() const;
                void finish();
                void setState(const state_type& next_state);
                AppMessage& getInitialMessage(){
                    return _initial_message;
                }
                const state_type& getCurrentState() const{
                    return _current_state;
                }
                void next(const state_type& state);
                void setTimerID(const timer_id_type& id, bool loop = false){
                    _timer_id = id;
                    _loop_timer = loop;
                }
                const timer_id_type& getTimerID() const{
                    return _timer_id;
                }
                bool isTimerSetted() const{
                    return (invalid_timer_id != _timer_id);
                }
                const bool& isLoopTimer() const{
                    return _loop_timer;
                }
                void resetTimer(){
                    _loop_timer = false;
                    _timer_id = invalid_timer_id;
                }
                const TaskTypeEnum& getTaskType() const{
                    return _task_type;
                }
                const session_id_type& getSessionID(){
                    return _session_id;
                }

                void attach(const uint16_t& queue_index){
                    _attached_index = queue_index;
                }
                const uint16_t& getQueueIndex() const{
                    return _attached_index;
                }
                WhisperSession(WhisperSession&& other);
                //
                const string& filename() const{
                    return _filename;
                }
                void filename(const string& value){
                    _filename = value;
                }
                const string& file_id() const{
                    return _file_id;
                }
                void file_id(const string& value){
                    _file_id = value;
                }

                const string& remote_ip() const{
                    return _remote_ip;
                }
                void remote_ip(const string& value){
                    _remote_ip = value;
                }
                const uint16_t& remote_port() const{
                    return _remote_port;
                }
                void remote_port(const uint16_t& value){
                    _remote_port = value;
                }

                const session_id_type& remote_session() const{
                    return _remote_session;
                }
                void remote_session(const session_id_type& value){
                    _remote_session = value;
                }

                const string& remote_file() const{
                    return _remote_file;
                }
                void remote_file(const string& value){
                    _remote_file = value;
                }

                const vector<uint16_t>& data_ports() const{
                    return _data_ports;
                }
                void data_ports(const vector<uint16_t>& value){
                    _data_ports = value;
                }

                const uint32_t& block_size() const{
                    return _block_size;
                }
                void block_size(const uint32_t& value){
                    _block_size = value;
                }

                const uint32_t& strip_length() const{
                    return _strip_length;
                }
                void strip_length(const uint32_t& value){
                    _strip_length = value;
                }

                const uint32_t& window_size() const{
                    return _window_size;
                }
                void window_size(const uint32_t& value){
                    _window_size = value;
                }
                const uint32_t& window_threshold() const{
                    return _window_threshold;
                }
                void window_threshold(const uint32_t& value){
                    _window_threshold = value;
                }

                WhisperSender& sender(){
                    return _sender;
                }
                WhisperReceiver& receiver(){
                    return _receiver;
                }
                uint32_t& counter(){
                    return _counter;
                }
                uint32_t& ack_counter(){
                    return _ack_counter;
                }

                uint32_t& offset(){
                    return _offset;
                }
                uint32_t& notify_counter(){
                    return _notify_counter;
                }
            private:
                typedef std::lock_guard< std::recursive_mutex > lock_type;
                bool _allocated;
                session_id_type _session_id;
                TaskTypeEnum _task_type;
                bool _initialed;
                state_type _current_state;
                AppMessage _initial_message;
                timer_id_type _timer_id;
                bool _loop_timer;
                bool _state_specified;
                mutable std::recursive_mutex _mutex;

                uint16_t _attached_index;
                string _filename;
                string _file_id;
                string _remote_ip;
                uint16_t _remote_port;
                session_id_type _remote_session;
                string _remote_file;
                vector<uint16_t> _data_ports;
                uint32_t _block_size;
                uint32_t _strip_length;
                uint32_t _window_size;
                uint32_t _window_threshold;

                WhisperSender _sender;
                WhisperReceiver _receiver;
                uint32_t _counter;
                uint32_t _ack_counter;
                uint32_t _offset;
                uint32_t _notify_counter;
        };
    }
}

#endif // WHISPER_SESSION_H

#ifndef WHISPER_TASK_H
#define WHISPER_TASK_H

#include <vector>
#include <boost/signals2.hpp>
#include <boost/bind.hpp>
#include <util/logging.h>
#include <transport/whisper_rule.h>

using std::vector;

namespace zhicloud{
    namespace transport{

        class WhisperTask
        {
            public:
                typedef WhisperSession session_type;
                typedef WhisperSession::state_type state_type;
                typedef WhisperRule::rule_handler rule_handler;
                typedef WhisperRule::ResultEnum result_type;
                typedef std::chrono::milliseconds duration_type;
                WhisperTask(const WhisperSession::TaskTypeEnum& task_type, const string& task_name);
                virtual ~WhisperTask();
                template < class T >
                void bindHandler(T* t){
                    onStart.connect(boost::bind(&T::onTaskStart, t, _1, _2));
                    onProgress.connect(boost::bind(&T::onTaskProgress, t, _1, _2, _3, _4, _5));
                    onSuccess.connect(boost::bind(&T::onTaskSuccess, t, _1, _2, _3));
                    onFail.connect(boost::bind(&T::onTaskFail, t, _1, _2));
                }

                template < class T >
                void bindFunction(T* obj){
                    function_set_timer.connect(boost::bind(&T::setTimer, obj, _1, _2));
                    function_set_loop_timer.connect(boost::bind(&T::setLoopTimer, obj, _1, _2));
                    function_clear_timer.connect(boost::bind(&T::clearTimer, obj, _1));
                    function_get_port.connect(boost::bind(&T::getReceivePorts, obj, _1));
                    function_send_message.connect(boost::bind(&T::sendMessage, obj, _1, _2, _3));
                }

                void initialSession(const AppMessage& msg, session_type& session);
                virtual void invokeSession(session_type& session);
                void processMessage(AppMessage& msg, session_type& session);
                void terminate(session_type& session);
                void releaseResource(session_type& session);
                const WhisperSession::TaskTypeEnum& type() const;
                const string& name() const;
            protected:
                void recordDataAck(session_type& session);
                void recordDataLost(session_type& session, const uint32_t& lost_count);

                void taskFail(session_type& session);
                void taskSuccess(session_type& session);
                void notifyStarted(session_type& session);
                void notifyProgress(session_type& session, const uint64_t& processed, const uint64_t& total, const uint64_t& speed);

                vector< uint64_t > getReceivePorts() const;

                bool sendMessage(AppMessage& msg, const string& remote_ip, const uint16_t& remote_port);
                void setTimer(session_type& session, const duration_type& timeout);
                void setLoopTimer(session_type& session, const duration_type& interval);
                void clearTimer(session_type& session);

                bool addState(const string& name, state_type& state);
                void addTransferRule(const state_type& state, const AppMessage::message_type& type,
                                                    const AppMessage::message_id_type& id, const result_type& result,
                                                    const rule_handler& handler, const state_type& next_state = session_type::getFinalState());
                virtual void onTerminate(session_type& session);
            private:
                void increaseWindowSize(session_type& session);
                void decreaseWindowSize(session_type& session);
            protected:
                zhicloud::util::logger_type logger;
            private:
                typedef WhisperSession::timer_id_type timer_id_type;
                typedef boost::signals2::signal< void (const uint32_t& , const uint16_t& ) > start_event_type;
                typedef boost::signals2::signal< void (const uint32_t& , const uint16_t&, const uint64_t&, const uint64_t&, const uint64_t& ) > progress_event_type;
                typedef boost::signals2::signal< void (const uint32_t& , const uint16_t&, const string& ) > success_event_type;
                typedef boost::signals2::signal< void (const uint32_t& , const uint16_t& ) > fail_event_type;
                start_event_type onStart;
                progress_event_type onProgress;
                success_event_type onSuccess;
                fail_event_type onFail;
                boost::signals2::signal< timer_id_type (const duration_type&, const uint64_t&) > function_set_timer;
                boost::signals2::signal< timer_id_type (const duration_type&, const uint64_t&) > function_set_loop_timer;
                boost::signals2::signal< bool (const timer_id_type&) > function_clear_timer;
                boost::signals2::signal< void (vector< uint64_t >&)> function_get_port;
                boost::signals2::signal< void (AppMessage&, const string&, const uint16_t&) > function_send_message;

                const static uint32_t max_lost;
                const static uint32_t default_windows_size;
                const static uint32_t increase_step;
                const static uint32_t default_threshold;
                WhisperSession::TaskTypeEnum _task_type;
                string _task_name;
                map< state_type, list < WhisperRule > > _state_map;
                map< state_type, string > _state_name_map;
        };

    }

}



#endif // WHISPER_TASK_H

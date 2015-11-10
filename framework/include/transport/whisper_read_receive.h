#ifndef WHIPSER_READ_RECEIVE_H
#define WHIPSER_READ_RECEIVE_H

#include <transport/whisper_task.h>

namespace zhicloud{
    namespace transport{
        class WhisperReadReceive : public WhisperTask
        {
            public:
                WhisperReadReceive();
                virtual ~WhisperReadReceive();
                virtual void invokeSession(session_type& session);
            private:
                void onPrepareSuccess(AppMessage& msg, session_type& session);
                void onPrepareTimeout(AppMessage& msg, session_type& session);
                void onDataReceived(AppMessage& msg, session_type& session);
                void onTransportFinished(AppMessage& msg, session_type& session);
                void onCheck(AppMessage& msg, session_type& session);
            private:
                const static uint32_t operate_timeout;
                const static uint32_t check_interval;
                const static uint32_t max_timeout;
        };
    }
}



#endif // WHIPSER_READ_RECEIVE_H

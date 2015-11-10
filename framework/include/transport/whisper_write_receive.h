#ifndef WHISPER_WRITE_RECEIVE_H
#define WHISPER_WRITE_RECEIVE_H

#include <transport/whisper_task.h>

namespace zhicloud{
    namespace transport{
        class WhisperWriteReceive : public WhisperTask
        {
            public:
                WhisperWriteReceive();
                virtual ~WhisperWriteReceive();
                virtual void invokeSession(session_type& session);
            private:
                void onTransportStart(AppMessage& msg, session_type& session);
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

#endif // WHISPER_WRITE_RECEIVE_H

#ifndef WHISPER_WRITE_SEND_H
#define WHISPER_WRITE_SEND_H

#include <transport/whisper_task.h>

namespace zhicloud{
    namespace transport{
        class WhisperWriteSend : public WhisperTask
        {
            public:
                WhisperWriteSend();
                virtual ~WhisperWriteSend();
                virtual void invokeSession(session_type& session);
            private:
                void onTransportReady(AppMessage& msg, session_type& session);
                void onPrepareTimeout(AppMessage& msg, session_type& session);
                void onDataConfirmed(AppMessage& msg, session_type& session);
                void onTransportFinished(AppMessage& msg, session_type& session);
                void onCheck(AppMessage& msg, session_type& session);
                void sendMoreData(session_type& session);
            private:
                const static uint64_t default_block_size;
                const static uint64_t default_strip_length;
                const static uint32_t operate_timeout;
                const static uint32_t check_interval;
                const static uint32_t max_timeout;
                const static uint32_t notify_interval;
        };

    }
}


#endif // WHISPER_WRITE_SEND_H

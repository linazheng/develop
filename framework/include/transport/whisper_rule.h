#ifndef WHISPER_RULE_H
#define WHISPER_RULE_H

#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <transport/app_message.h>
#include <transport/whisper_session.h>

namespace zhicloud{
    namespace transport{
        class WhisperRule
        {
            public:
                typedef boost::signals2::signal< void (AppMessage&, WhisperSession&) > event_type;
                typedef event_type::slot_type rule_handler;
                typedef WhisperSession::state_type state_type;
                enum class ResultEnum:uint16_t
                {
                    success = 0,
                    fail = 1,
                    any = 2,
                };

                WhisperRule(const AppMessage::message_type& type, const AppMessage::message_id_type& id, const ResultEnum& result,
                                    const rule_handler& handler, const state_type& next_state);
                virtual ~WhisperRule();
                bool isMatch(const AppMessage& message) const;
                void invoke(AppMessage& message, WhisperSession& session);
                const state_type& getNextState() const;
            private:
                AppMessage::message_type _type;
                AppMessage::message_id_type _id;
                ResultEnum _result;
                state_type _next_state;
                event_type _onInvoke;
        };
    }
}


#endif // WHISPER_RULE_H

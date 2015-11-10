#ifndef PROCESSRULE_H
#define PROCESSRULE_H

#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <transport/app_message.h>

using zhicloud::transport::AppMessage;

namespace zhicloud{
    namespace transaction{
        template < class session_type>
        class ProcessRule
        {
            public:
                typedef boost::signals2::signal< void (AppMessage&, session_type&) > event_type;
                typedef typename event_type::slot_type rule_handler;
                typedef typename session_type::state_type state_type;
                enum class Result:uint32_t
                {
                    success = 0,
                    fail = 1,
                    any = 2,
                };

                ProcessRule(const AppMessage::message_type& type, const AppMessage::message_id_type& id, const Result& result,
                            const rule_handler& handler, const state_type& next_state = state_type::finish):
                    message_type(type), message_id(id), message_result(result), next_state(next_state)
                {
                    onInvoke.connect(handler);
                }
                virtual ~ProcessRule(){
                }
                bool isMatch(const AppMessage& message) const
                {
                    if(message.type != message_type)
                        return false;
                    if(message.id != message_id)
                        return false;
                    if(message_result == Result::any)
                        return true;
                    if((message.success)&&(Result::success == message_result))
                        return true;
                    if(!(message.success)&&(Result::fail == message_result))
                        return true;
                    return false;
                }
                void invoke(AppMessage& message, session_type& session){
                    onInvoke(message, session);
                }
                state_type getNextState() const{
                    return next_state;
                }
            private:
                AppMessage::message_type message_type;
                AppMessage::message_id_type message_id;
                Result message_result;
                state_type next_state;
                event_type onInvoke;

        };
    }
}


#endif // PROCESSRULE_H

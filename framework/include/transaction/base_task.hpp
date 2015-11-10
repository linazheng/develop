#ifndef BASE_TASK_HPP_INCLUDED
#define BASE_TASK_HPP_INCLUDED
#include <exception>
#include <string>
#include <map>
#include <list>
#include <boost/bind.hpp>
#include <boost/signals2.hpp>
#include <util/define.hpp>
#include <util/logging.h>
#include <transport/app_message.h>
#include <transaction/process_rule.hpp>

using namespace std;
using zhicloud::transport::AppMessage;
using namespace zhicloud::util;

namespace zhicloud{
    namespace transaction{
        template < class S, class P >
        class BaseTask{
        private:
            typedef typename S::timer_id_type timer_id_type;
            typedef uint32_t timeout_type;
            typedef typename S::session_id_type session_id_type;
            typedef boost::signals2::signal< bool (AppMessage&) > message_event_1;
            typedef boost::signals2::signal< bool (const AppMessage&) > const_message_event_1;
            typedef boost::signals2::signal< bool (AppMessage&, const string&) > message_event_2;
            typedef boost::signals2::signal< bool (const int32_t&) > timer_event_1;
            typedef boost::signals2::signal< int32_t (const timeout_type&, const session_id_type&) > timer_event_2;

        public:
            typedef S session_type;
            typedef P proxy_type;
            typedef typename session_type::state_type state_type;
            typedef typename session_type::task_id_type task_id_type;
            typedef ProcessRule< session_type > rule_type;
            typedef typename rule_type::rule_handler rule_handler;
            typedef typename rule_type::Result result_type;
            typedef typename AppMessage::message_id_type message_id_type;

            BaseTask(const task_id_type& task_id, const string& task_name,
            		 const message_id_type& resp_msg, proxy_type* proxy)
            {
                logger = getLogger("BaskTask");
                this->task_id = task_id;
                this->task_name = task_name;
                this->message_id = resp_msg;
                state_map[session_type::getInitialState()] = std::move(list < rule_type >());
                state_name_map[session_type::getInitialState()] = "initial";
                state_name_map[session_type::getFinishState()] = "finish";
//                state_map.emplace(state_type::initial, std::move(list < rule_type >()));
                invoke_send_message.connect(boost::bind(&proxy_type::sendMessage, proxy, _1, _2));
                invoke_send_to_self.connect(boost::bind(&proxy_type::putMessage, proxy, _1));
                invoke_send_to_domain_server.connect(boost::bind(&proxy_type::sendToDomainServer, proxy, _1));

                invoke_set_timer.connect(boost::bind(&proxy_type::setTimer, proxy, _1, _2));
                invoke_set_loop_timer.connect(boost::bind(&proxy_type::setLoopTimer, proxy, _1, _2));
                invoke_clear_timer.connect(boost::bind(&proxy_type::clearTimer, proxy, _1));
            }
            virtual ~BaseTask(){
            }
            void initialSession(const AppMessage& msg, session_type& session){
                session.initial(msg);
            }
            virtual void invokeSession(session_type& session){
                throw std::runtime_error("must override BaseTask::invokeSession");
            }
            void processMessage(AppMessage& msg, session_type& session){
                if((AppMessage::message_type::EVENT == msg.type)&&((uint32_t)EventEnum::terminate == msg.id)){
                    terminate(session);
                    return;
                }
                if((AppMessage::message_type::EVENT == msg.type)&&((uint32_t)EventEnum::timeout == msg.id)){
                    if(msg.sequence != session.getTimerID()){
                        logger->warn(boost::format("[%08X]ignore timeout event with timer id %d(current %d)")
                                     %session.getSessionID() %msg.sequence %session.getTimerID());
                        return;
                    }
                    //clear single timer id
                    if(!session.isLoopTimer()){
                        session.resetTimer();
                    }
                }
                state_type current_state = session.getCurrentState();
                if(state_map.end() == state_map.find(current_state)){
                    logger->warn(boost::format("[%08X]task '%s':no rule defined for state %d")
                                 %session.getSessionID() %task_name %(uint32_t)current_state);
                    return;
                }
                for(rule_type& rule:state_map[current_state]){
                    if(rule.isMatch(msg)){
                        //match
                        rule.invoke(msg, session);
                        session.next(rule.getNextState());
                        return;
                    }
                }
                logger->warn(boost::format("[%08X]task '%s':no rule defined for state '%s', message(%d)")
                             %session.getSessionID() %task_name %state_name_map[current_state] %msg.id);
            }
            void terminate(session_type& session){
                onTerminate(session);
                clearTimer(session);
                session.finish();
            }
            task_id_type getTaskID() const{
                return task_id;
            }
            void releaseResource(session_type& session){
                clearTimer(session);
            }
        protected:
            bool sendMessage(AppMessage& msg, const string& receiver){
                return *invoke_send_message(msg, receiver);
            }

            bool sendMessageToSelf(const AppMessage& msg){
                return *invoke_send_to_self(msg);
            }

            bool sendToDomainServer(AppMessage& msg){
                return *invoke_send_to_domain_server(msg);
            }

            void setTimer(session_type& session, const uint32_t& interval){
                if(session.isTimerSetted()){
                    logger->warn(boost::format("[%08X]old timer %d override by set timer")
                                     %session.getSessionID() %session.getTimerID());
                }
                timer_id_type timer_id = *invoke_set_timer(interval, session.getSessionID());
                session.setTimerID(timer_id);
            }

            void setLoopTimer(session_type& session, const uint32_t& interval){
                if(session.isTimerSetted()){
                    logger->warn(boost::format("<Whisper>[%08X]old timer %d override by set loop timer")
                                     %session.getSessionID() %session.getTimerID());
                }
                timer_id_type timer_id = *invoke_set_loop_timer(interval, session.getSessionID());
                session.setTimerID(timer_id, true);
            }

            void clearTimer(session_type& session){
                if(session.isTimerSetted()){
                    timer_id_type timer_id = session.getTimerID();
                    if(!*invoke_clear_timer(timer_id)){
                        logger->warn(boost::format("[%08X]clear timer fail, timer id %d")
                                     %session.getSessionID() %timer_id);
                    }
                    session.resetTimer();
                }
            }
            void taskFail(session_type& session){
                AppMessage response(AppMessage::message_type::RESPONSE, (RequestEnum)message_id);
                response.session = session.getRequestSession();
                response.success = false;
                session.finish();
                sendMessage(response, session.getRequestModule());
            }

            void reportFail(session_type& session){
                AppMessage response(AppMessage::message_type::RESPONSE, (RequestEnum)message_id);
                response.session = session.getRequestSession();
                response.success = false;
                sendMessage(response, session.getRequestModule());
            }


            bool addState(const string& name, state_type& state){
            	//check name
            	for(typename std::pair< state_type, string > item:state_name_map){
            		if(0 == name.compare(item.second))
            		{
            			//exists name
            			logger->error(boost::format("state '%s' already exists in task '%s'")
            						  %name %task_name);
            			return false;
            		}
            	}
            	//find id
            	typename map< state_type, list < rule_type > >::iterator ir;
            	for(state = session_type::getInitialState(); state < session_type::getFinishState(); state++){
            		ir = state_map.find(state);
            		if(state_map.end() == ir){
            			//new state
            			state_map[state] = std::move(list < rule_type >());
            			state_name_map[state] = name;
            			logger->info(boost::format("task '%s' add state '%s'(%d)")
            						 %task_name %name %state);
            			return true;
            		}
            	}
            	logger->error(boost::format("can't allocate state '%s' for task '%s'")
            	              %name %task_name);
                return false;
            }

            void addTransferRule(const state_type& state, const AppMessage::message_type& type,
                                 const AppMessage::message_id_type& id, const result_type& result,
                                 const rule_handler& handler, const state_type& next_state = session_type::getFinishState())
            {
                if(state_map.end() == state_map.find(state))
                {
                    //new state
                	logger->error(boost::format("add rule fail, invalid state %d in task '%s'")
                	              %state %task_name);
                	return;
                }

                //append
                state_map[state].emplace_back(type, id, result, handler, next_state);
            }
            virtual void onTerminate(session_type& session){
                //need override
            }

        private:
            BaseTask();
            BaseTask(const BaseTask& other);
            BaseTask& operator=(const BaseTask& other);

            BaseTask(BaseTask&& other);
        protected:
            zhicloud::util::logger_type logger;
        private:
            task_id_type task_id;
            string task_name;
            message_id_type message_id;
            map< state_type, list < rule_type > > state_map;
            map< state_type, string > state_name_map;
            message_event_2 invoke_send_message;
            const_message_event_1 invoke_send_to_self;
            message_event_1 invoke_send_to_domain_server;
            timer_event_2 invoke_set_timer;
            timer_event_2 invoke_set_loop_timer;
            timer_event_1 invoke_clear_timer;

        };
    }
}

#endif // BASIC_TASK_HPP_INCLUDED

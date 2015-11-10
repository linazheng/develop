#ifndef TASK_SESSION_HPP_INCLUDED
#define TASK_SESSION_HPP_INCLUDED

#include <transaction/transaction.hpp>
#include <transaction/base_session.hpp>

#include "Task_type.hpp"

namespace zhicloud
{
    namespace control_server{
        class TaskSession : public transaction::BaseSession<TaskType> {
        public:
            TaskSession()
            {
                onReset();
            }
            TaskSession(const session_id_type &session_id):BaseSession<TaskType>(session_id)
            {
                onReset();
            }

            void onReset()
            {
                BaseSession::reset();
                _data_server.clear();
                _statistic_server.clear();
                _target_list.clear();
                _target.clear();
                _offset = 0;
                _total = 0;
                _remote_session = 0;
                _counter = 0;

            }
        private:
            string _data_server;
            string _statistic_server;
            vector<string> _target_list;
            string _target;
            uint32_t _offset;
            uint32_t _total;
            uint32_t _remote_session;
            uint32_t _counter;
        };

    }
}


#endif // TASK_SESSION_HPP_INCLUDED

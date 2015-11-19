#ifndef QUERYCOMPUTEPOOLTASK_H
#define QUERYCOMPUTEPOOLTASK_H

#include "task_session.hpp"
#include "computepool_manager.h"
#include "status_manager.h"

namespace zhicloud
{
    namespace control_server{
        class QueryComputePoolTask : public transaction::BaseTask<TaskSession, NodeService>
        {
        public:
        QueryComputePoolTask(NodeService *messsage_handler,ComputePoolManager& computepool_manager,StatusManager& status_manager);


        void invokeSession(TaskSession &session);

        protected:

        private:
            util::logger_type _logger;
            ComputePoolManager& _computepool_manager;
            StatusManager& _status_manager;

        };
}
}

#endif // QUERYCOMPUTEPOOLTASK_H

#ifndef CLIENTTRANSMANAGER_H
#define CLIENTTRANSMANAGER_H

#include <transaction/transaction.hpp>
#include <transaction/base_manager.hpp>
#include <transaction/base_task.hpp>
#include <service/node_service.h>
#include "task_session.hpp"
#include "computepool_manager.h"

namespace zhicloud{

    namespace control_server{

        class ClientTransManager: public transaction::BaseManager<transaction::BaseTask<TaskSession, NodeService> >
        {
        public:
            ClientTransManager(NodeService* messsage_handler,ComputePoolManager& computepool_manager,const uint32_t& work_thread);
            ~ClientTransManager();

        protected:

        private:
            const static uint32_t session_count;
            ComputePoolManager& _computepool_manager;
        };
    }

}



#endif // CLIENTTRANSMANAGER_H

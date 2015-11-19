#ifndef CLIENTTRANSMANAGER_H
#define CLIENTTRANSMANAGER_H

#include <transaction/transaction.hpp>
#include <transaction/base_manager.hpp>
#include <transaction/base_task.hpp>
#include <service/node_service.h>
#include <util/logging.h>
#include "task_session.hpp"
#include "computepool_manager.h"
#include "status_manager.h"
#include "config_manager.h"
#include "service_manager.h"
#include "expire_manager.h"

namespace zhicloud{

    namespace control_server{

        class ClientTransManager: public transaction::BaseManager<transaction::BaseTask<TaskSession, NodeService> >
        {
        public:
            ClientTransManager(NodeService* messsage_handler,
                ComputePoolManager& computepool_manager,
                StatusManager& status_manager,
                ConfigManager& config_manager,
                ServiceManager& service_manager,
                ExpireManager& expire_manager,
                const uint32_t& work_thread);
            ~ClientTransManager();

        protected:

        private:
            util::logger_type _logger;
            const static uint32_t session_count;
            ComputePoolManager& _computepool_manager;
            StatusManager& _status_manager;
            ConfigManager& _config_manager;
            ServiceManager& _service_manager;
            ExpireManager& _expire_manager;

        };
    }

}



#endif // CLIENTTRANSMANAGER_H

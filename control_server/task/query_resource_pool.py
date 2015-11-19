#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryResourcePoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager,
                 compute_pool_manager, storage_pool_manager,
                 address_manager, port_manager):
        self.status_manager = status_manager
        self.compute_pool_manager = compute_pool_manager
        self.storage_pool_manager = storage_pool_manager
        self.address_manager = address_manager
        self.port_manager = port_manager
        logger_name = "task.query_resource_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_resource_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        ##[idle, allocated]
        address_statistic = self.address_manager.statisticStatus()
        ##[idle, allocated]
        port_statistic = self.port_manager.statisticStatus()
        ##[stop, warn, error, running]
        storage_statistic = self.storage_pool_manager.statisticStatus()
        ##[stop, warn, error, running]
        stop = 0
        warn = 0
        error = 0
        run = 0
        for compute_pool in self.compute_pool_manager.queryAllPool():
            if self.status_manager.containsComputePoolStatus(compute_pool.uuid):
                status = self.status_manager.getComputePoolStatus(compute_pool.uuid)
                stop += status.node[0]
                warn += status.node[1]
                error += status.node[2]
                run += status.node[3]
        compute_statistic = [stop, warn, error, run]

        count = [address_statistic, port_statistic,
                 compute_statistic, storage_statistic]

        total_compute_node = sum(compute_statistic)
        self.info("[%08X] <query_resource_pool> success, %d compute node(s) available"%
                  (session.session_id, total_compute_node))
        
        response = getResponse(RequestDefine.query_resource_pool)
        response.session = session.request_session
        response.success = True
        
        response.setUIntArrayArray(ParamKeyDefine.count, count)
        
        self.sendMessage(response, session.request_module)
        session.finish()

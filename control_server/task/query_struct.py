#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryStructTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager,
                 service_manager):
        self.status_manager = status_manager
        self.service_manager = service_manager
        logger_name = "task.query_struct"
        BaseTask.__init__(self, task_type, RequestDefine.query_struct,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        ##server
        stop = 0
        warn = 0
        error = 0
        run = 0
        for server_status in self.status_manager.getAllServerRoomStatus():
            stop += server_status.server[0]
            warn += server_status.server[1]
            error += server_status.server[2]
            run += server_status.server[3]
        
        ##[stop, warn, error, running]
        server_statistic = [stop, warn, error, run]

        ##service
        ##[stop, warn, error, running]
        service_statistic = self.service_manager.statisticStatus()
        ##[stop, warn, error, running]
        router_statistic = [0, 0, 0, 0]
        ##[stop, warn, error, running]
        firewall_statistic = [0, 0, 0, 0]
        ##[stop, warn, error, running]
        switch_statistic = [0, 0, 0, 0]

        count = [server_statistic, service_statistic,
                 router_statistic, firewall_statistic,
                 switch_statistic]

        total_server = sum(server_statistic)
        total_service = sum(service_statistic)
        self.info("[%08X]query resource pool success, %d server/ %d service available"%
                  (session.session_id, total_server, total_service))
        
        response = getResponse(RequestDefine.query_struct)
        response.session = session.request_session
        response.success = True
        
        response.setUIntArrayArray(ParamKeyDefine.count, count)
        
        self.sendMessage(response, session.request_module)
        session.finish()

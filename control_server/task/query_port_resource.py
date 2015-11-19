#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from port_resource import *

class QueryPortResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 port_manager):
        self.port_manager = port_manager
        logger_name = "task.query_port_resource"
        BaseTask.__init__(self, task_type, RequestDefine.query_port_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool_id = request.getString(ParamKeyDefine.pool)
        self.info("[%08X]receive query port resource request from '%s', pool '%s'"%(
                session.session_id, session.request_module,
                pool_id))

        resource_list = self.port_manager.queryResource(pool_id)
        if 0 == len(resource_list):
            self.error("[%08X]query port resource fail, no address resource available"%
                       session.session_id)
            self.taskFail(session)
            return
        ip = []
        status = []
        count = []
        for resource in resource_list:
            ip.append(resource.ip)
            if resource.enable:
                status.append(1)
            else:
                status.append(0)
                
            available, total = resource.statistic()
            count.append([available, total])

        self.info("[%08X]query port resource success, %d port resource(s) available"%
                  (session.session_id, len(resource_list)))
        
        response = getResponse(RequestDefine.query_port_resource)
        response.session = session.request_session
        response.success = True
        response.setStringArray(ParamKeyDefine.ip, ip)
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setUIntArrayArray(ParamKeyDefine.count, count)
        
        self.sendMessage(response, session.request_module)
        session.finish()

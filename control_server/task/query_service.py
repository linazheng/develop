#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryServiceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 service_manager):
        self.service_manager = service_manager
        logger_name = "task.query_service"
        BaseTask.__init__(self, task_type, RequestDefine.query_service,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        service_type = session.initial_message.getUInt(ParamKeyDefine.type)
        service_group = session.initial_message.getString(ParamKeyDefine.group)
        service_list = self.service_manager.queryService(service_type, service_group)
        count = len(service_list)
        
        response = getResponse(RequestDefine.query_service)
        response.session = session.request_session
        response.success = True

        name = []
        ip = []
        port = []
        status = []
        version = []
        server = []
        disk_type = []
        for service in service_list:
            name.append(service.name)
            ip.append(service.ip)
            port.append(service.port)
            status.append(service.status)
            version.append(service.version)
            server.append(service.server)
            disk_type.append(service.disk_type)

        response.setStringArray(ParamKeyDefine.name, name)                
        response.setStringArray(ParamKeyDefine.ip, ip)                
        response.setUIntArray(ParamKeyDefine.port, port)                 
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setStringArray(ParamKeyDefine.version, version)
        response.setStringArray(ParamKeyDefine.server, server)
        response.setUIntArray(ParamKeyDefine.disk_type, disk_type)
            
        self.info("[%08X]query service success, %d service(s) available for service type %d, group '%s'"%(
            session.session_id, count, service_type, service_group))
        self.sendMessage(response, session.request_module)
        session.finish()

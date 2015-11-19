#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from host_forwarder import *

class QueryForwarderTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 service_manager):
        self.service_manager = service_manager
        logger_name = "task.query_forwarder"
        BaseTask.__init__(self, task_type, RequestDefine.query_forwarder,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        forwarder_type = session.initial_message.getUInt(ParamKeyDefine.type)
        self.info("[%08X]receive query forwarder request from '%s', forwarder type %d"%(
                session.session_id, session.request_module, forwarder_type))
        if ForwarderTypeEnum.domain == forwarder_type:
            self.error("[%08X]query forwarder by domain bound type not supported"%(
                session.session_id))
            self.taskFail(session)
            return
        forwarder_list = self.forwarder_manager.query(forwarder_type)
        if 0 == len(forwarder_list):
            self.error("[%08X]query forwarder fail, no forwarder in type %d"%(
                session.session_id, forwarder_type))
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.get_forwarder)
        response.session = session.request_session
        response.success = True

        uuid = []
        ip = []
        host_id = []
        host_name = []
        port = []
        domain = []
        status = []
        for forwarder in forwarder_list:
            uuid.append(forwarder.uuid)
            ip.append(forwarder.public_ip)
            host_id.append(forwarder.host_id)
            host_name.append(forwarder.host_name)
            port_list = []
            for forwarder_port in forwarder.port:
                port_list.append(forwarder_port.public_port)
            port.append(port_list)
            if forwarder.enable:
                status.append(1)
            else:
                status.append(0)            
 
        response.setUInt(ParamKeyDefine.type, forwarder.type)
        response.setStringArray(ParamKeyDefine.uuid, uuid)                
        response.setStringArrayArray(ParamKeyDefine.ip, ip)
        response.setStringArray(ParamKeyDefine.host, host_id)                
        response.setStringArray(ParamKeyDefine.name, host_name)                
        response.setUIntArrayArray(ParamKeyDefine.port, port)                
        response.setStringArray(ParamKeyDefine.domain, domain)                
        response.setUIntArray(ParamKeyDefine.status, status)                
            
        self.info("[%08X]query forwarder success, %d forwarder available"%(
            session.session_id, len(forwarder_list)))
        self.sendMessage(response, session.request_module)
        session.finish()

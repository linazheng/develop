#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryWhisperTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 service_manager):
        self.service_manager = service_manager
        logger_name = "task.query_whisper"
        BaseTask.__init__(self, task_type, RequestDefine.query_whisper,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        service_list = self.service_manager.getAllWhisper()
        count = len(service_list)
        
        response = getResponse(RequestDefine.query_whisper)
        response.session = session.request_session
        response.success = True

        name = []
        service_type = []
        ip = []
        port = []
        for whisper in service_list:
            name.append(whisper.name)
            service_type.append(whisper.type)            
            ip.append(whisper.ip)
            port.append(whisper.port)
 
        response.setStringArray(ParamKeyDefine.name, name)                
        response.setUIntArray(ParamKeyDefine.type, service_type)
        response.setStringArray(ParamKeyDefine.ip, ip)                
        response.setUIntArray(ParamKeyDefine.port, port)                 
            
        self.info("[%08X]query whipser success, %d whisper service(s) available"%(
            session.session_id, count))
        self.sendMessage(response, session.request_module)
        session.finish()

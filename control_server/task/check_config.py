#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class CheckConfigTask(BaseTask):
    
    check_type_forwarder = 0
    check_level_global = 0
    check_level_list = 1
    
    def __init__(self, task_type, messsage_handler,
                 forwarder_manager):
        self.forwarder_manager = forwarder_manager
        logger_name = "task.check_config"
        BaseTask.__init__(self, task_type, RequestDefine.check_config,
                          messsage_handler, logger_name)
    
    
    def invokeSession(self, session):
        request = session.initial_message
        check_type = request.getUInt(ParamKeyDefine.type)
        check_level = request.getUInt(ParamKeyDefine.level)
        
        if CheckConfigTask.check_type_forwarder != check_type:
            self.error("[%08X]check config fail, invalid type %d"%(
                session.session_id, check_type))
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.check_config)
        response.session = session.request_session
        response.setUInt(ParamKeyDefine.type, check_type)
        response.setUInt(ParamKeyDefine.level, check_level)
            
        if CheckConfigTask.check_level_global == check_level:
            ##global
            response.success = True
            crc = self.forwarder_manager.getCRC()
            response.setUInt(ParamKeyDefine.identity, crc)
            
        elif CheckConfigTask.check_level_list == check_level:
            ##list
            id_list, crc_list = self.forwarder_manager.getAllCRC()
            response.success = True
            response.setStringArray(ParamKeyDefine.target, id_list)
            response.setUIntArray(ParamKeyDefine.identity, crc_list)
            count = len(id_list)
            
        else:
            self.error("[%08X]check config fail, invalid level %d"%(
                session.session_id, check_level))
            self.taskFail(session)
            return
        
        self.sendMessage(response, session.request_module)
        session.finish()

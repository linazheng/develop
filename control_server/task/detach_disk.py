#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class DetachDiskTask(BaseTask):
    operate_timeout = 10
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.detach_disk"
        BaseTask.__init__(self, task_type, RequestDefine.detach_disk,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.detach_disk, result_success,
                             self.onDetachSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.detach_disk, result_fail,
                             self.onDetachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDetachTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        index = request.getUInt(ParamKeyDefine.index)
        self.info("[%08X]receive detach disk request from '%s', host id '%s', index %d"%(
            session.session_id, session.request_module,
            uuid, index))            
        
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]detach disk fail, invalid id '%s'"%(
                session.session_id, uuid))
            self.taskFail(session)
            return        

        ##get container
        host = self.config_manager.getHost(uuid)
        service_name = host.container
        
        self.info("[%08X]redirect detach disk '%s'('%s') to compute node '%s'"%(
            session.session_id, host.name, host.uuid, service_name))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)

    def onDetachSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]detach disk success, id '%s'"%(
            session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onDetachFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]detach disk fail, id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)
        
    def onDetachTimeout(self, msg, session):
        self.error("[%08X]detach disk timeout, id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)

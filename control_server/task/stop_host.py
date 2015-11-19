#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class StopHostTask(BaseTask):
    operate_timeout = 10
    def __init__(self, task_type, messsage_handler,
                 config_manager, compute_pool_manager):
        self.config_manager = config_manager
        self.compute_pool_manager = compute_pool_manager
        logger_name = "task.stop_host"
        BaseTask.__init__(self, task_type, RequestDefine.stop_host,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_host, result_success,
                             self.onStopSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.stop_host, result_fail,
                             self.onStopFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onStopTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]stop host fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        host = self.config_manager.getHost(uuid)
        service_name = host.container
            
        self.info("[%08X]request stop host '%s'('%s') to compute node '%s'"%
                       (session.session_id, host.name, host.uuid, service_name))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)

    def onStopSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]stop host success, id '%s'"%
                       (session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onStopFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]stop host fail, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onStopTimeout(self, msg, session):
        self.info("[%08X]stop host timeout, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

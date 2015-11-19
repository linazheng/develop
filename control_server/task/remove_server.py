#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class RemoveServerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.remove_server"
        BaseTask.__init__(self, task_type, RequestDefine.remove_server,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_server, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_server, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)
        if not self.config_manager.containsServer(uuid):
            self.error("[%08X]remove server fail, '%s' not exists"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        self.info("[%08X]request remove server '%s' to data server"%
                       (session.session_id, uuid))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)
        if not self.config_manager.removeServer(session.target):
            self.error("[%08X]remove server fail, id '%s'"%
                       (session.session_id, session.target))
            self.taskFail(session)
            return
        self.info("[%08X]remove server success, id '%s'"%
                       (session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]remove server fail, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onRemoveTimeout(self, msg, session):
        self.info("[%08X]remove server timeout, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

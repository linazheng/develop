#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class ResetHostTask(BaseTask):
    operate_timeout = 5

    def __init__(self, task_type, messsage_handler, config_manager):
        self.config_manager = config_manager
        logger_name = "task.reset_host"
        BaseTask.__init__(self, task_type, RequestDefine.reset_host, messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.reset_host, result_success, self.onResetSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.reset_host, result_fail, self.onResetFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onResetTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X] <reset_host> reset host fail, invalid id '%s'" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        host = self.config_manager.getHost(uuid)

        self.info("[%08X] <reset_host> request reset host '%s'('%s') to compute node '%s'" %
                       (session.session_id, host.name, host.uuid, host.container))

        request.session = session.session_id
        self.sendMessage(request, host.container)

        self.setTimer(session, self.operate_timeout)

    def onResetSuccess(self, msg, session):
        self.clearTimer(session)
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)

        self.info("[%08X] <reset_host> reset host success, id '%s'" %
                       (session.session_id, uuid))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onResetFail(self, msg, session):
        self.clearTimer(session)

        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)

        self.info("[%08X] <reset_host> reset host fail, id '%s'" %
                  (session.session_id, uuid))

        self.taskFail(session)

    def onResetTimeout(self, msg, session):
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)

        self.info("[%08X] <reset_host> reset host timeout, id '%s'" %
                  (session.session_id, uuid))

        self.taskFail(session)

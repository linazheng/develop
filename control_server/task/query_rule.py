#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class QueryRuleTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler):
        logger_name = "task.query_rule"
        BaseTask.__init__(self, task_type, RequestDefine.query_rule, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_rule, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_rule, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)

        self.info("[%08X]receive query rule request, target '%s'" %
                  (session.session_id, target))

        if target not in self.message_handler.intelligent_router:
            self.error("[%08X]query rule fail, no intelligent router named '%s'" %
                       (session.session_id, target))
            self.taskFail(session)
            return

        request.session = session.session_id
        self.sendMessage(request, target)
        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)
        mode = msg.getUIntArray(ParamKeyDefine.mode)
        if mode == None:
            self.info("[%08X]query rule success, no rule is available" % session.session_id)
        else:
            self.info("[%08X]query rule success, %d rule is available" %
                      (session.session_id, len(mode)))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]query rule fail" % session.session_id)
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X]query rule timeout" % session.session_id)
        self.taskFail(session)

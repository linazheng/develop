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

class RemoveRuleTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler):
        logger_name = "task.remove_rule"
        BaseTask.__init__(self, task_type, RequestDefine.remove_rule, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.remove_rule, result_success, self.onSuccess, state_initial)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.remove_rule, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)
        mode = request.getUInt(ParamKeyDefine.mode)
        ip = request.getStringArray(ParamKeyDefine.ip)
        port = request.getUIntArray(ParamKeyDefine.port)

        self.info("[%08X]receive remove rule request, add ip(%s) port(%s) in mode '%d' into '%s'" %
                  (session.session_id, ip, port, mode, target))

        if len(target) != 0 and target not in self.message_handler.intelligent_router:
            self.error("[%08X]remove rule fail, no intelligent router named '%s'" %
                       (session.session_id, target))
            self.taskFail(session)
            return

        session.target_list = []

        if len(target) == 0:
            for intelligent_router in self.message_handler.intelligent_router:
                session.target_list.append(intelligent_router)
        else:
            session.target_list.append(target)

        request.session = session.session_id
        for intelligent_router in session.target_list:
            self.sendMessage(request, intelligent_router)

        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        sender = msg.sender
        self.info("[%08X]remove rule from '%s' success" %
                  (session.session_id, sender))

        if sender in session.target_list:
            session.target_list.remove(sender)

        if len(session.target_list) == 0:
            self.clearTimer(session)
            self.info("[%08X]remove rule success" % session.session_id)

            msg.session = session.request_session
            self.sendMessage(msg, session.request_module)
            session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        sender = msg.sender
        self.error("[%08X]remove rule from '%s' fail" %
                   (session.session_id, sender))
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X]remove rule timeout, target: %s" %
                   (session.session_id, ", ".join(session.target_list)))
        self.taskFail(session)


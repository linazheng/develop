#!/usr/bin/python
from transaction.base_task import BaseTask
from service.message_define import RequestDefine
from service.message_define import ParamKeyDefine
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from transaction.state_define import result_success
from transaction.state_define import result_fail
from service.message_define import EventDefine
from transaction.state_define import result_any
from common import dict_util

class AddRuleTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler):
        logger_name = "task.add_rule"
        BaseTask.__init__(self, task_type, RequestDefine.add_rule, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.add_rule, result_success, self.onSuccess, state_initial)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.add_rule, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        
        target = request.getString(ParamKeyDefine.target)
        mode   = request.getUInt(ParamKeyDefine.mode)
        ip     = request.getStringArray(ParamKeyDefine.ip)
        port   = request.getUIntArray(ParamKeyDefine.port)
        
        v_parameter = {}
        v_parameter["target"] = target
        v_parameter["mode"]   = mode
        v_parameter["ip"]     = ip
        v_parameter["port"]   = port

        self.info("[%08X] <add_rule> receive add rule request, parameter: %s" % (session.session_id, dict_util.toDictionary(v_parameter, max_deep=3)))

        if len(target) != 0 and target not in self.message_handler.intelligent_router:
            self.error("[%08X] <add_rule> add rule fail, no intelligent router named '%s'" %
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
        self.info("[%08X] <add_rule> add rule into '%s' success" %
                  (session.session_id, sender))

        if sender in session.target_list:
            session.target_list.remove(sender)

        if len(session.target_list) == 0:
            self.clearTimer(session)
            self.info("[%08X] <add_rule> add rule success" % session.session_id)

            msg.session = session.request_session
            self.sendMessage(msg, session.request_module)
            session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        sender = msg.sender
        self.error("[%08X] <add_rule> add rule into '%s' fail" %
                   (session.session_id, sender))
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X] <add_rule> add rule timeout, target: %s" %
                   (session.session_id, ", ".join(session.target_list)))
        self.taskFail(session)


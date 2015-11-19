#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *

class QueryServiceDetailTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler):
        logger_name = "task.query_service_detail"
        BaseTask.__init__(self, task_type, RequestDefine.query_service_detail,
                          messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_service_detail, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_service_detail, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        target = getString(request, ParamKeyDefine.target)
        begin_date = getString(request, ParamKeyDefine.begin)
        end_date = getString(request, ParamKeyDefine.end)
        server = getString(request, ParamKeyDefine.server)

        if target == None or 0 == len(target):
            self.error("[%08X]query service detail fail, must specify target" % (
                session.session_id))
            self.taskFail(session)
            return

        if begin_date == None or 0 == len(begin_date):
            self.error("[%08X]query service detail fail, invalid begin date '%s'" % (
                session.session_id, begin_date))
            self.taskFail(session)
            return

        if end_date == None or 0 == len(end_date):
            self.error("[%08X]query service detail fail, invalid end date '%s'" % (
                session.session_id, end_date))
            self.taskFail(session)
            return

        if server == None or 0 == len(server):
            self.error("[%08X] query service detail fail, invalid server '%s'" %
                       (session.session_id, server))
            self.taskFail(session)
            return

        session.statistic_server = server
        self.info("[%08X]request query service detail to server '%s', origin requester '%s'[%08X]" %
                       (session.session_id, session.statistic_server,
                        session.request_module, session.request_session))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, server)

    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query service detail success, server '%s'" %
                       (session.session_id, session.statistic_server))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query service detail fail, server '%s'" %
                  (session.session_id, session.statistic_server))
        self.taskFail(session)

    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query service detail timeout, server '%s'" %
                  (session.session_id, session.statistic_server))
        self.taskFail(session)

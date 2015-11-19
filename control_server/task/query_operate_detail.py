#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *

class QueryOperateDetailTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler, config_manager):
        logger_name = "task.query_operate_detail"
        self.config_manager = config_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_operate_detail,
                          messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_operate_detail, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_operate_detail, result_fail,
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
            self.error("[%08X]query operate detail fail, must specify target" % (
                session.session_id))
            self.taskFail(session)
            return

        if begin_date == None or 0 == len(begin_date):
            self.error("[%08X]query operate detail fail, invalid begin date '%s'" % (
                session.session_id, begin_date))
            self.taskFail(session)
            return

        if end_date == None or 0 == len(end_date):
            self.error("[%08X]query operate detail fail, invalid end date '%s'" % (
                session.session_id, end_date))
            self.taskFail(session)
            return

        if server == None or 0 == len(server):
            self.error("[%08X] query operate detail fail, invaild server '%s'" %
                       (session.session_id, server))
            self.taskFail(session)
            return


        session.statistic_server = server
        self.info("[%08X]request query operate detail to server '%s', origin requester '%s'[%08X]" %
                       (session.session_id, session.statistic_server,
                        session.request_module, session.request_session))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, server)

    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query operate detail success, server '%s'" %
                       (session.session_id, session.statistic_server))
        
        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)
        #get room uuid, rack uuid, server name
        if self.config_manager.containsServer(target):
            server = self.config_manager.getServer(target)
            msg.setString(ParamKeyDefine.server_name,server.name)
            msg.setString(ParamKeyDefine.rack, server.rack)
            
            if self.config_manager.containsServerRack(server.rack):
                rack = self.config_manager.getServerRack(server.rack)
                msg.setString(ParamKeyDefine.room, rack.server_room)

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query operate detail fail, server '%s'" %
                  (session.session_id, session.statistic_server))
        self.taskFail(session)

    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query operate detail timeout, server '%s'" %
                  (session.session_id, session.statistic_server))
        self.taskFail(session)

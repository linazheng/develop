#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from data.domain_config import *

class QueryOperateSummaryTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler, config_manager):
        logger_name = "task.query_operate_summary"
        self.config_manager = config_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_operate_summary,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_operate_summary, result_success,
                             self.onQuerySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_operate_summary, result_fail,
                             self.onQueryFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        target_list = getStringArray(request, ParamKeyDefine.target)
        begin_date = getString(request, ParamKeyDefine.begin)
        end_date = getString(request, ParamKeyDefine.end)
        server = getString(request, ParamKeyDefine.server)
        
        if target_list == None or 0 == len(target_list):
            self.error("[%08X]query operate summary fail, must specify target"%(
                session.session_id))
            self.taskFail(session)
            return
        
        ##date format YYYYMMDD
        if begin_date == None or 8 != len(begin_date):
            self.error("[%08X]query operate summary fail, invalid begin date '%s'"%(
                session.session_id, begin_date))
            self.taskFail(session)
            return
        
        if end_date == None or 8 != len(end_date):
            self.error("[%08X]query operate summary fail, invalid end date '%s'"%(
                session.session_id, end_date))
            self.taskFail(session)
            return
        
        if server == None or 0 == len(server):
            self.error("[%08X] query operate summary fail, invalid server '%s'" %
                       (session.session_id, server))
            self.taskFail(session)
            return
                
        session.statistic_server = server
        self.info("[%08X]request query operate summary to server '%s', origin requester '%s'[%08X]"%
                       (session.session_id, session.statistic_server,
                        session.request_module, session.request_session))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, server)

    def onQuerySuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query operate summary success, server '%s'"%
                       (session.session_id, session.statistic_server))
        
        request = session.initial_message
        target = request.getStringArray(ParamKeyDefine.target)
        room_list = []
        rack_list = []
        server_name_list = []
        #get room uuid, rack uuid, server name
        for server_id in target:
            if self.config_manager.containsServer(server_id):
                server = self.config_manager.getServer(server_id)
                server_name_list.append(server.name)
                rack_list.append(server.rack)
                
                if self.config_manager.containsServerRack(server.rack):
                    rack = self.config_manager.getServerRack(server.rack)
                    room_list.append(rack.server_room)
                else:
                    room_list.append("")
        
        msg.setStringArray(ParamKeyDefine.room, room_list)
        msg.setStringArray(ParamKeyDefine.rack, rack_list)
        msg.setStringArray(ParamKeyDefine.server_name, server_name_list)

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onQueryFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]query operate summary fail, server '%s'"%
                  (session.session_id, session.statistic_server))
        self.taskFail(session)
        
    def onQueryTimeout(self, msg, session):
        self.info("[%08X]query operate summary timeout, server '%s'"%
                  (session.session_id, session.statistic_server))
        self.taskFail(session)

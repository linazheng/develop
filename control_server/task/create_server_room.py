#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from server_room_info import *

class CreateServerRoomTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.create_server_room"
        BaseTask.__init__(self, task_type, RequestDefine.create_server_room,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_server_room, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_server_room, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        server_room = getString(request, ParamKeyDefine.name)
        self.info("[%08X]request create server room '%s' to data server"%
                       (session.session_id, server_room))
        session.target = server_room
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        info = ServerRoomInfo()
        info.uuid = msg.getString(ParamKeyDefine.uuid)
        info.name = session.initial_message.getString(ParamKeyDefine.name)
        if not self.config_manager.addServerRoom(info):
            self.error("[%08X]create server room fail, name '%s'"%
                       (session.session_id, session.target))
            self.taskFail(session)
            return
        self.info("[%08X]create server room success, name '%s'"%
                       (session.session_id, session.target))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create server room fail, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create server room timeout, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

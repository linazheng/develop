#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from server_rack_info import *

class CreateServerRackTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.create_server_rack"
        BaseTask.__init__(self, task_type, RequestDefine.create_server_rack,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_server_rack, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_server_rack, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        server_rack = getString(request, ParamKeyDefine.name)
        self.info("[%08X]request create server rack '%s' to data server"%
                       (session.session_id, server_rack))
        session.target = server_rack
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        info = ServerRackInfo()
        info.uuid = msg.getString(ParamKeyDefine.uuid)
        info.name = session.initial_message.getString(ParamKeyDefine.name)
        info.server_room = session.initial_message.getString(ParamKeyDefine.room)
        if not self.config_manager.addServerRack(info):
            self.error("[%08X]create server rack fail, name '%s'"%
                       (session.session_id, info.name))
            self.taskFail(session)
            return
        self.info("[%08X]create server rack success, name '%s'"%
                       (session.session_id, info.name))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create server rack fail, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create server rack timeout, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

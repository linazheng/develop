#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from server_info import *

class AddServerTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.add_server"
        BaseTask.__init__(self, task_type, RequestDefine.add_server,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_server, result_success,
                             self.onAddSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_server, result_fail,
                             self.onAddFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        server = getString(request, ParamKeyDefine.name)
        self.info("[%08X]request add server '%s' to data server"%
                       (session.session_id, server))
        session.target = server
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onAddSuccess(self, msg, session):
        self.clearTimer(session)
        info = ServerInfo()
        info.uuid = msg.getString(ParamKeyDefine.uuid)
        info.name = session.initial_message.getString(ParamKeyDefine.name)
        info.rack = session.initial_message.getString(ParamKeyDefine.rack)
        if not self.config_manager.addServer(info):
            self.error("[%08X]add server fail, name '%s'"%
                       (session.session_id, info.name))
            self.taskFail(session)
            return
        self.info("[%08X]add server success, name '%s'"%
                       (session.session_id, info.name))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]add server rack fail, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onAddTimeout(self, msg, session):
        self.info("[%08X]add server rack timeout, name '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

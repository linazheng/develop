#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from server_rack_info import *

class ModifyServerRackTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.modify_server_rack"
        BaseTask.__init__(self, task_type, RequestDefine.modify_server_rack,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_server_rack, result_success,
                             self.onModifySuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_server_rack, result_fail,
                             self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)
        if not self.config_manager.containsServerRack(uuid):
            self.error("[%08X]modify server rack fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        session.target = uuid
        self.info("[%08X]request modify server rack '%s' to data server"%
                       (session.session_id, uuid))
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        info = ServerRackInfo()
        info.uuid = session.initial_message.getString(ParamKeyDefine.uuid)
        info.name = session.initial_message.getString(ParamKeyDefine.name)
        info.server_room = session.initial_message.getString(ParamKeyDefine.room)
        if not self.config_manager.modifyServerRack(info.uuid, info):
            self.error("[%08X]modify server rack fail, name '%s'"%
                       (session.session_id, info.name))
            self.taskFail(session)
            return
        self.info("[%08X]modify server rack success, name '%s'"%
                       (session.session_id, info.name))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]modify server rack fail, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onModifyTimeout(self, msg, session):
        self.info("[%08X]modify server rack timeout, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

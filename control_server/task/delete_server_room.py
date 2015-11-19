#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class DeleteServerRoomTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.delete_server_room"
        BaseTask.__init__(self, task_type, RequestDefine.delete_server_room,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_server_room, result_success,
                             self.onDeleteSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_server_room, result_fail,
                             self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = getString(request, ParamKeyDefine.uuid)
        if not self.config_manager.containsServerRoom(uuid):
            self.error("[%08X]delete server room fail, '%s' not exists"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        self.info("[%08X]request delete server room '%s' to data server"%
                       (session.session_id, uuid))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendToDomainServer(request)

    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)
        if not self.config_manager.removeServerRoom(session.target):
            self.error("[%08X]delete server room fail, id '%s'"%
                       (session.session_id, session.target))
            self.taskFail(session)
            return
        self.info("[%08X]delete server room success, id '%s'"%
                       (session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]delete server room fail, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onDeleteTimeout(self, msg, session):
        self.info("[%08X]delete server room timeout, id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

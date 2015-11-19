#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class DeleteSnapshotPoolTask(BaseTask):
    
    timeout = 5
    
    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.delete_snapshot_pool"
        BaseTask.__init__(self, task_type, RequestDefine.delete_snapshot_pool, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.delete_snapshot_pool,
                             result_success,
                             self.onSuccess,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.delete_snapshot_pool,
                             result_fail,
                             self.onFail,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.EVENT,
                             EventDefine.timeout,
                             result_any,
                             self.onTimeout,
                             state_finish
                             )
    
    def invokeSession(self, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive delete snapshot pool request from '%s', uuid '%s'" %
                  (session.session_id, session.request_module, uuid))

        snapshot_pool = self.snapshot_pool_manager.getSnapshotPoolDuplication(uuid)
        if snapshot_pool != None:
            data_index = snapshot_pool.data_index
        else:
            data_index = self.message_handler.getDefaultDataIndex()
        
        request.session = session.session_id
        if not self.message_handler.sendMessage(request, data_index):
            self.taskFail(session)
            self.info("[%08X]delete snapshot pool fail. uuid '%s'" %
                      (session.session_id, uuid))
            return

        self.setTimer(session, self.timeout)
        
    def onSuccess(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.snapshot_pool_manager.removeSnapshotPool(uuid)
        self.info("[%08X]delete snapshot pool success. uuid '%s'" %
                  (session.session_id, uuid))

        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.uuid)
        self.error("[%08X]delete snapshot pool fail. uuid '%s'" %
                   (session.session_id, snapshot_pool))
        self.taskFail(session)

    def onTimeout(self, response, session):
        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]delete snapshot pool timeout. uuid '%s'" %
                  (session.session_id, snapshot_pool))
        self.taskFail(session)
        
        
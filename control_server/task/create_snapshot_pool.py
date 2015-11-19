#!/usr/bin/python
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from transaction.state_define import result_fail
from service.message_define import EventDefine
from transaction.state_define import result_any
from service.message_define import ParamKeyDefine
from snapshot_pool import SnapshotPool

class CreateSnapshotPoolTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.create_snapshot_pool"
        BaseTask.__init__(self, task_type, RequestDefine.create_snapshot_pool, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.create_snapshot_pool,
                             result_success,
                             self.onSuccess,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.create_snapshot_pool,
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
        snapshot_pool = request.getString(ParamKeyDefine.name)
        self.info("[%08X]receive create snapshot pool request from '%s', name '%s'" %
                  (session.session_id, session.request_module, snapshot_pool))

        request.session = session.session_id
        data_index = self.message_handler.getDefaultDataIndex()
        if not self.message_handler.sendMessage(request, data_index):
            self.taskFail(session)
            return

        self.setTimer(session, self.timeout)
        
    def onSuccess(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        name = request.getString(ParamKeyDefine.name)        
        uuid = response.getString(ParamKeyDefine.uuid)
        target = response.sender
        
        snapshot_pool = SnapshotPool()
        snapshot_pool.data_index = target
        snapshot_pool.name = name
        snapshot_pool.uuid = uuid
        self.snapshot_pool_manager.addSnapshotPool(snapshot_pool)
        
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        
        self.info("[%08X]create snapshot pool success. name '%s'" %
                  (session.session_id, name))
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.name)
        self.error("[%08X]create snapshot pool fail. name '%s'" %
                   (session.session_id, snapshot_pool))
        self.taskFail(session)

    def onTimeout(self, response, session):
        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.name)
        self.info("[%08X]create snapshot pool timeout. name '%s'" %
                  (session.session_id, snapshot_pool))
        self.taskFail(session)


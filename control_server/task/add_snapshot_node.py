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
from snapshot_node import SnapshotNode

class AddSnapshotNodeTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.add_snapshot_node"
        BaseTask.__init__(self, task_type, RequestDefine.add_snapshot_node, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.add_snapshot_node,
                             result_success,
                             self.onSuccess,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.add_snapshot_node,
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
        pool = request.getString(ParamKeyDefine.pool)
        node = request.getString(ParamKeyDefine.name)
        self.info("[%08X]receive add snapshot node request from '%s', pool '%s', node '%s'" %
                  (session.session_id, session.request_module, pool, node))

        snapshot_pool = self.snapshot_pool_manager.getSnapshotPoolDuplication(pool)
        if snapshot_pool != None:
            data_index = snapshot_pool.data_index
        else:
            data_index = self.message_handler.getDefaultDataIndex()

        request.session = session.session_id
        if not self.message_handler.sendMessage(request, data_index):
            self.taskFail(session)
            return

        self.setTimer(session, self.timeout)

    def onSuccess(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        name = request.getString(ParamKeyDefine.name)

        snapshot_node = SnapshotNode()
        snapshot_node.name = name
        self.snapshot_pool_manager.addSnapshotNode(pool, snapshot_node)

        self.info("[%08X]add snapshot node success. pool '%s', node '%s'" %
                  (session.session_id, pool, name))

        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.pool)
        node = request.getString(ParamKeyDefine.name)
        self.error("[%08X]add snapshot node fail. pool '%s', node '%s'" %
                   (session.session_id, snapshot_pool, node))
        self.taskFail(session)

    def onTimeout(self, response, session):
        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.pool)
        node = request.getString(ParamKeyDefine.name)
        self.info("[%08X]add snapshot node timeout. pool '%s', node '%s'" %
                  (session.session_id, snapshot_pool, node))
        self.taskFail(session)


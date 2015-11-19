#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from service.message_define import getRequest
from snapshot_pool import SnapshotPool
from task.task_type import initial_snapshot_node
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class InitialSnapshotPoolTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager, control_trans_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        self.control_trans_manager = control_trans_manager
        logger_name = "task.initial_snapshot_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_snapshot_pool, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.query_snapshot_pool,
                             result_success,
                             self.onSuccess,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.query_snapshot_pool,
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
        target = request.getString(ParamKeyDefine.target)
        self.info("[%08X]<initial_snapshot_pool>start to initialize snapshot pool from '%s'." %
                  (session.session_id, target))

        new_request = getRequest(RequestDefine.query_snapshot_pool)
        new_request.session = session.session_id
        if not self.message_handler.sendMessage(new_request, target):
            session.finish()
            return

        self.setTimer(session, self.timeout)
        
    def onSuccess(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)

        name_array = response.getStringArray(ParamKeyDefine.name)
        uuid_array = response.getStringArray(ParamKeyDefine.uuid)
        node_array = response.getUIntArrayArray(ParamKeyDefine.node)
        snapshot_array = response.getUIntArrayArray(ParamKeyDefine.snapshot)
        cpu_count_array = response.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage_array = response.getFloatArray(ParamKeyDefine.cpu_usage)
        memory_array = response.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage_array = response.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume_array = response.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage_array = response.getFloatArray(ParamKeyDefine.disk_usage)
        status_array = response.getUIntArray(ParamKeyDefine.status)

        for i in xrange(len(uuid_array)):
            snapshot_pool = SnapshotPool()
            snapshot_pool.data_index = target
            snapshot_pool.name = name_array[i]
            snapshot_pool.uuid = uuid_array[i]
            snapshot_pool.node = node_array[i]
            snapshot_pool.snapshot = snapshot_array[i]
            snapshot_pool.cpu_count = cpu_count_array[i]
            snapshot_pool.cpu_usage = cpu_usage_array[i]
            snapshot_pool.memory = memory_array[i]
            snapshot_pool.memory_usage = memory_usage_array[i]
            snapshot_pool.disk_volume = disk_volume_array[i]
            snapshot_pool.disk_usage = disk_usage_array[i]
            snapshot_pool.status = status_array[i]

            self.snapshot_pool_manager.addSnapshotPool(snapshot_pool)

            # initialize snapshot node
            if sum(snapshot_pool.node) != 0:  # node exists
                node_request = getRequest(RequestDefine.invalid)
                node_request.setString(ParamKeyDefine.pool, snapshot_pool.uuid)
                node_request.setString(ParamKeyDefine.target, target)
                session_id = self.control_trans_manager.allocTransaction(initial_snapshot_node)
                self.control_trans_manager.startTransaction(session_id, node_request)


        self.info("[%08X]<initial_snapshot_pool>success to initialize snapshot pool from '%s'. %d snapshot pools available" %
                  (session.session_id, target, len(uuid_array)))

        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)

        self.error("[%08X]<initial_snapshot_pool>fail to initialize snapshot pool from '%s'." %
                   (session.session_id, target))
        session.finish()

    def onTimeout(self, response, session):
        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)

        self.warn("[%08X]<initial_snapshot_pool>initialize snapshot pool timeout from '%s'." %
                  (session.session_id, target))
        session.finish()

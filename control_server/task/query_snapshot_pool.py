#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from snapshot_pool import SnapshotPool
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class QuerySnapshotPoolTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.query_snapshot_pool"
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
        self.info("[%08X]receive query snapshot pool request from '%s'" %
                  (session.session_id, session.request_module))

        request.session = session.session_id
        data_index = self.message_handler.getDefaultDataIndex()
        if not self.message_handler.sendMessage(request, data_index):
            self.taskFail(session)
            return

        self.setTimer(session, self.timeout)
        
    def onSuccess(self, response, session):
        self.clearTimer(session)
        
        target = response.sender
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

        response.session = session.request_session
        self.sendMessage(response, session.request_module)

        self.info("[%08X]query snapshot pool success. %d snapshot pools available" %
                  (session.session_id, len(uuid_array)))
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        self.error("[%08X]query snapshot pool fail." %
                   session.session_id)
        self.taskFail(session)

    def onTimeout(self, response, session):
        self.info("[%08X]query snapshot pool timeout." %
                  session.session_id)
        self.taskFail(session)


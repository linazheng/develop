#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from snapshot_node import SnapshotNode
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class QuerySnapshotNodeTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.query_snapshot_node"
        BaseTask.__init__(self, task_type, RequestDefine.query_snapshot_node, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.query_snapshot_node,
                             result_success,
                             self.onSuccess,
                             state_finish
                             )

        self.addTransferRule(state_initial,
                             AppMessage.RESPONSE,
                             RequestDefine.query_snapshot_node,
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
        self.info("[%08X]receive query snapshot node request from '%s', pool '%s'" %
                  (session.session_id, session.request_module, pool))

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
        
        name_array = response.getStringArray(ParamKeyDefine.name)
        status_array = response.getUIntArray(ParamKeyDefine.status)
        cpu_count_array = response.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage_array = response.getFloatArray(ParamKeyDefine.cpu_usage)
        memory_array = response.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage_array = response.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume_array = response.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage_array = response.getFloatArray(ParamKeyDefine.disk_usage)
        ip_array = response.getStringArray(ParamKeyDefine.ip)

        snapshot_node_list = []
        for i in xrange(len(name_array)):
            snapshot_node = SnapshotNode()
            snapshot_node.name = name_array[i]
            snapshot_node.status = status_array[i]
            snapshot_node.cpu_count = cpu_count_array[i]
            snapshot_node.cpu_usage = cpu_usage_array[i]
            snapshot_node.memory = memory_array[i]
            snapshot_node.memory_usage = memory_usage_array[i]
            snapshot_node.disk_volume = disk_volume_array[i]
            snapshot_node.disk_usage = disk_usage_array[i]
            snapshot_node.ip = ip_array[i]

            snapshot_node_list.append(snapshot_node)

        self.snapshot_pool_manager.addSnapshotNodeList(pool, snapshot_node_list)
        
        self.info("[%08X]query snapshot node success. pool '%s', %d snapshot nodes available" %
                  (session.session_id, pool, len(name_array)))

        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.pool)
        self.error("[%08X]query snapshot node fail. pool '%s'" %
                   (session.session_id, snapshot_pool))
        self.taskFail(session)

    def onTimeout(self, response, session):
        request = session.initial_message
        snapshot_pool = request.getString(ParamKeyDefine.pool)
        self.info("[%08X]query snapshot node timeout. pool '%s'" %
                  (session.session_id, snapshot_pool))
        self.taskFail(session)


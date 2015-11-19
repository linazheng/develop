#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from service.message_define import ParamKeyDefine
from service.message_define import getRequest
from snapshot_node import SnapshotNode

class InitialSnapshotNodeTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, snapshot_pool_manager):
        self.snapshot_pool_manager = snapshot_pool_manager
        logger_name = "task.initial_snapshot_node"
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
        target = request.getString(ParamKeyDefine.target)

        new_request = getRequest(RequestDefine.query_snapshot_node)
        new_request.session = session.session_id
        new_request.setString(ParamKeyDefine.pool, pool)

        if not self.message_handler.sendMessage(new_request, target):
            session.finish()
            return

#         self.info("[%08X]<initial_snapshot_node>start to initialize snapshot node from '%s'. pool '%s'" %
#                   (session.session_id, target, pool))
        self.setTimer(session, self.timeout)
        
    def onSuccess(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        target = request.getString(ParamKeyDefine.target)

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

#         self.info("[%08X]<initial_snapshot_node>success to initialize snapshot node from '%s'. pool '%s'" %
#                   (session.session_id, target, pool))
        session.finish()

    def onFail(self, response, session):
        self.clearTimer(session)

        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        target = request.getString(ParamKeyDefine.target)
        self.error("[%08X]<initial_snapshot_node>fail to initialize snapshot node from '%s'. pool '%s'" %
                   (session.session_id, target, pool))

        session.finish()

    def onTimeout(self, response, session):
        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        target = request.getString(ParamKeyDefine.target)
        self.warn("[%08X]<initial_snapshot_node>initialize snapshot node timeout from '%s'. pool '%s'" %
                   (session.session_id, target, pool))

        session.finish()


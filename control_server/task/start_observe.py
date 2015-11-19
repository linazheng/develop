#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from host_status import *
from server_status import *
import datetime

class StartObserveTask(BaseTask):
    operate_timeout = 30
    def __init__(self, task_type, messsage_handler, status_manager, config_manager, service_manager):
        self.status_manager = status_manager
        self.config_manager = config_manager
        self.service_manager = service_manager
        logger_name = "task.start_observe"
        BaseTask.__init__(self, task_type, RequestDefine.start_observe,
                          messsage_handler, logger_name)

        stObserve = 2
        self.addState(stObserve)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.start_observe, result_success, self.onStartSuccess, stObserve)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.start_observe, result_fail, self.onStartFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onStartTimeout)

        # stObserve
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.host_status, result_any, self.onHostStatus, stObserve)
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.host_added, result_any, self.onHostAdded, stObserve)
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.host_removed, result_any, self.onHostRemoved, stObserve)
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.host_status_changed, result_any, self.onHostStatusChanged, stObserve)
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.server_status, result_any, self.onServerStatus, stObserve)
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.timeout, result_any, self.onObserveTimeout, stObserve)


    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        receiver = request.getString(ParamKeyDefine.name)
        target = request.getString(ParamKeyDefine.target)
        self.info("[%08X] <start_observe> request observe to remote node '%s', receiver '%s'" % (
            session.session_id, target, receiver))

        request = getRequest(RequestDefine.start_observe)
        request.session = session.session_id
        request.setString(ParamKeyDefine.name, receiver)
        self.sendMessage(request, target)
        self.setTimer(session, self.operate_timeout)

    def onStartSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <start_observe> started" % (
            session.session_id))

        self.setTimer(session, self.operate_timeout)

    def onStartFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <start_observe> start fail" % (
            session.session_id))
        session.finish()

    def onStartTimeout(self, event, session):
        self.info("[%08X] <start_observe> start timeout" % (
            session.session_id))
        session.finish()

    def onHostStatus(self, event, session):
# #        self.info("[%08X]on host status"%(
# #            session.session_id))
        count = event.getUInt(ParamKeyDefine.count)
        if 0 == count:
            return
        server_id = event.getString(ParamKeyDefine.server)
        timestamp = event.getString(ParamKeyDefine.timestamp)

        uuid = event.getStringArray(ParamKeyDefine.uuid)

        ip = event.getStringArrayArray(ParamKeyDefine.ip)
        cpu_count = event.getUIntArray(ParamKeyDefine.cpu_count)
        cpu_usage = event.getFloatArray(ParamKeyDefine.cpu_usage)
        memory = event.getUIntArrayArray(ParamKeyDefine.memory)
        memory_usage = event.getFloatArray(ParamKeyDefine.memory_usage)
        disk_volume = event.getUIntArrayArray(ParamKeyDefine.disk_volume)
        disk_usage = event.getFloatArray(ParamKeyDefine.disk_usage)
        disk_io = event.getUIntArrayArray(ParamKeyDefine.disk_io)
        network_io = event.getUIntArrayArray(ParamKeyDefine.network_io)
        speed = event.getUIntArrayArray(ParamKeyDefine.speed)
        host_status = event.getUIntArray(ParamKeyDefine.status)

        status_list = []
        for i in range(count):
            status = HostStatus()
            status.cpu_count = cpu_count[i]
            status.cpu_usage = cpu_usage[i]
            status.memory = memory[i]
            status.memory_usage = memory_usage[i]
            status.disk_volume = disk_volume[i]
            status.disk_usage = disk_usage[i]
            status.disk_io = disk_io[i]
            status.network_io = network_io[i]
            status.speed = speed[i]
            status.timestamp = timestamp
            status.server = server_id
            status.uuid = uuid[i]
            status.ip = ip[i]
            status.status = host_status[i]

            status_list.append(status)

        self.status_manager.updateHostStatus(status_list)

    def onHostAdded(self, event, session):
        host_status = HostStatus()
        host_status.uuid = event.getString(ParamKeyDefine.uuid)
        name = event.getString(ParamKeyDefine.name)
        if self.config_manager.containsHost(host_status.uuid):
            host_info = self.config_manager.getHost(host_status.uuid)
            host_status.cpu_count = host_info.cpu_count
            host_status.memory = [host_info.memory, host_info.memory]
            total_disk_volume = sum(host_info.disk_volume)
            host_status.disk_volume = [total_disk_volume, total_disk_volume]
            host_status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            host_status.ip = [host_info.server_ip, host_info.vpc_ip if bool(host_info.network) else host_info.public_ip]

        self.status_manager.addHostStatus(host_status)
        self.debug("[%08X] <start_observe> host added, uuid '%s', name '%s'" %
                   (session.session_id, host_status.uuid, name))

    def onHostRemoved(self, event, session):
        host_id = event.getString(ParamKeyDefine.uuid)
        name = event.getString(ParamKeyDefine.name)
        self.status_manager.removeHostStatus(host_id)
        self.debug("[%08X] <start_observe> host removed, uuid '%s', name '%s'" %
                   (session.session_id, host_id, name))

    def onHostStatusChanged(self, event, session):
        host_id = event.getString(ParamKeyDefine.uuid)
        host_status = event.getUInt(ParamKeyDefine.status)
        self.status_manager.changeHostStatus(host_id, host_status)
        self.debug("[%08X] <start_observe> host status changed, uuid '%s', new status '%d'" %
                   (session.session_id, host_id, host_status))

    def onServerStatus(self, event, session):
        self.clearTimer(session)

        status = ServerStatus()
        status.ip = event.getString(ParamKeyDefine.ip)
        status.uuid = event.getString(ParamKeyDefine.uuid)
        status.cpu_count = event.getUInt(ParamKeyDefine.cpu_count)
        status.cpu_usage = event.getFloat(ParamKeyDefine.cpu_usage)
        status.memory = event.getUIntArray(ParamKeyDefine.memory)
        status.memory_usage = event.getFloat(ParamKeyDefine.memory_usage)
        status.disk_volume = event.getUIntArray(ParamKeyDefine.disk_volume)
        status.disk_usage = event.getFloat(ParamKeyDefine.disk_usage)
        status.disk_io = event.getUIntArray(ParamKeyDefine.disk_io)
        status.network_io = event.getUIntArray(ParamKeyDefine.network_io)
        status.speed = event.getUIntArray(ParamKeyDefine.speed)
        status.timestamp = event.getString(ParamKeyDefine.timestamp)
        self.status_manager.updateServerStatus(status.uuid, status)

        self.setTimer(session, self.operate_timeout)

    def onObserveTimeout(self, event, session):
        self.warn("[%08X] <start_observe> timeout" % (
            session.session_id))
# #        session.finish()

    def onTerminate(self, session):
        """
        overridable
        """
        self.clearTimer(session)
        self.info("[%08X] <start_observe> terminated" % (
            session.session_id))
        
        request = session.initial_message
        node_client_name = request.getString(ParamKeyDefine.target)
        ##remove server status
        if self.service_manager.containsService(node_client_name):
            service = self.service_manager.getService(node_client_name)
            self.status_manager.removeServerStatus(service.server)
        
        ##remove host status
        host_list = self.config_manager.queryHosts(node_client_name)
        for host in host_list:
            self.status_manager.removeHostStatus(host.uuid)



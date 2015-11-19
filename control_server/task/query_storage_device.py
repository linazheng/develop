#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class QueryStorageDeviceTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, service_manager):
        logger_name = "task.query_storage_device"
        self.service_manager = service_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_storage_device, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_device, result_success, self.onSuccess, state_initial)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_device, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        level = request.getUInt(ParamKeyDefine.level)
        target = request.getString(ParamKeyDefine.target)
        disk_type = request.getUInt(ParamKeyDefine.disk_type)

        self.info("[%08X] <query_storage_device> receive request, level '%d', target '%s', disk_type '%d'" %
                  (session.session_id, level, target, disk_type))

        if level != 1:
            self.warn("[%08X] <query_storage_device> query fail, no support level '%d'" %
                      (session.session_id, level))
            self.taskFail(session)
            return

        if not self.service_manager.containsService(target):
            self.error("[%08X] <query_storage_device> query fail, invalid target '%s'" %
                       (session.session_id, target))
            self.taskFail(session)
            return

        if disk_type not in (ComputeStorageTypeEnum.local, ComputeStorageTypeEnum.cloud, ComputeStorageTypeEnum.nas, ComputeStorageTypeEnum.ip_san):
            self.error("[%08X] <query_storage_device> query fail, invalid disk type '%d'" %
                       (session.session_id, disk_type))
            self.taskFail(session)
            return

        request.session = session.session_id
        self.sendMessage(request, target)
        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <query_storage_device> success" %
                  (session.session_id))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <query_storage_device> fail" %
                   (session.session_id))
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X] <query_storage_device> timeout" %
                   (session.session_id))
        self.taskFail(session)


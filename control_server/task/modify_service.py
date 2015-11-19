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

class ModifyServiceTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_hander, service_manager):
        logger_name = "task.modify_service"
        self.service_manager = service_manager
        BaseTask.__init__(self, task_type, RequestDefine.modify_service, message_hander, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        service_type = request.getUInt(ParamKeyDefine.type)
        target = request.getString(ParamKeyDefine.target)
        disk_type = request.getUInt(ParamKeyDefine.disk_type)

        self.info("[%08X] <modify_service> receive request, type '%d', target '%s', disk_type '%d'" %
                  (session.session_id, service_type, target, disk_type))

        if not self.service_manager.containsService(target):
            self.error("[%08X] <modify_service> fail, invalid target '%s'" %
                       (session.session_id, target))
            self.taskFail(session)
            return
        service = self.service_manager.getService(target)

        if service_type != service.type:
            self.error("[%08X] <modify_service> fail, service '%s'(type '%d') and type '%d' not match" %
                       (session.session_id, service.name, service.type, service_type))
            self.taskFail(session)
            return

        if disk_type not in (ComputeStorageTypeEnum.local, ComputeStorageTypeEnum.cloud, ComputeStorageTypeEnum.nas, ComputeStorageTypeEnum.ip_san):
            self.error("[%08X] <modify_service> fail, invalid disk type '%d'" %
                       (session.session_id, disk_type))
            self.taskFail(session)
            return

        request.session = session.session_id
        self.sendMessage(request, target)
        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <modify_service> success" %
                  (session.session_id))

        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)
        disk_type = request.getUInt(ParamKeyDefine.disk_type)

        # #modify cache
        service = self.service_manager.getService(target)
        if service != None:
            service.disk_type = disk_type

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <modify_service> fail" %
                   (session.session_id))
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X] <modify_service> timeout" %
                   (session.session_id))
        self.taskFail(session)


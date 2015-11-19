#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from service.message_define import getRequest

class SyncServiceStatusTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, service_manager):
        logger_name = "task.synch_service_status"
        self.service_manager = service_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_service, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_service, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_service, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)

        self.info("[%08X] <synch_service_status> start to synch, target '%s'" %
                  (session.session_id, target))

        query_request = getRequest(RequestDefine.query_service)
        query_request.session = session.session_id
        self.sendMessage(query_request, target)
        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)

        request = session.initial_message
        target = request.getString(ParamKeyDefine.target)
        disk_type = msg.getUInt(ParamKeyDefine.disk_type)

        self.info("[%08X] <synch_service_status> success, service '%s', disk_type '%d'" %
                  (session.session_id, target, disk_type))

        # #synch service status
        self.service_manager.updateService(target, disk_type)
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <synch_service_status> fail" % 
                   (session.session_id))
        session.finish()

    def onTimeout(self, msg, session):
        self.error("[%08X] <synch_service_status> timeout" %
                   (session.session_id))
        session.finish()

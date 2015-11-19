#!/usr/bin/python
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from transaction.state_define import result_success
from transaction.state_define import result_fail
from service.message_define import EventDefine
from transaction.state_define import result_any
from service.message_define import getResponse

class QueryHostBackupTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, config_manager):
        logger_name = "task.query_host_backup"
        self.config_manager = config_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_host_backup, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host_backup, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host_backup, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive query host backup request, uuid '%s'" %
                  (session.session_id, uuid))

        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]query host backup fail, host '%s' does not exist" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return

        host_info = self.config_manager.getHost(uuid)

        request.session = session.session_id
        self.sendMessage(request, host_info.container)

        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)

        index = msg.getUIntArray(ParamKeyDefine.index)
        disk_volume = msg.getUIntArray(ParamKeyDefine.disk_volume)
        timestamp = msg.getStringArray(ParamKeyDefine.timestamp)

        self.info("[%08X]query host backup success, %d backup is available in host '%s'" %
                  (session.session_id, len(disk_volume), uuid))

        response = getResponse(RequestDefine.query_host_backup)
        response.session = session.request_session
        response.success = True
        response.setUIntArray(ParamKeyDefine.index, index)
        response.setUIntArray(ParamKeyDefine.disk_volume, disk_volume)
        response.setStringArray(ParamKeyDefine.timestamp, timestamp)
        self.sendMessage(response, session.request_module)

        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)

        self.error("[%08X]query host backup fail, host '%s'" %
                  (session.session_id, uuid))

        self.taskFail(session)

    def onTimeout(self, msg, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)

        self.error("[%08X]query host backup timeout, host '%s'" %
                   (session.session_id, uuid))

        self.taskFail(session)


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
from transport.whisper import Whisper
from whisper_service import WhisperService

class StorageServerSyncTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, message_handler, service_manager):
        logger_name = "task.storage_server_sync"
        self.service_manager = service_manager
        BaseTask.__init__(self, task_type, RequestDefine.invalid, message_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_whisper, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_whisper, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        request = session.initial_message
        storage_server = request.getString(ParamKeyDefine.target)

        if not bool(storage_server):
            session.finish()
            return

        query_whisper_request = getRequest(RequestDefine.query_whisper)
        query_whisper_request.session = session.session_id
        self.sendMessage(query_whisper_request, storage_server)

        self.setTimer(session, self.timeout)

    def onSuccess(self, msg, session):
        self.clearTimer(session)
        request = session.initial_message
        storage_server = request.getString(ParamKeyDefine.target)

        count = msg.getUInt(ParamKeyDefine.count)
        ip = msg.getString(ParamKeyDefine.ip)
        port = msg.getUInt(ParamKeyDefine.port)
        group = msg.getUIntArray(ParamKeyDefine.group)

        whisper_list = []
        if count > 1:
            # # add whisper by group param
            for port_info in group:
                whisper = WhisperService()
                whisper.ip = ip
                whisper.port = port_info
                whisper_list.append(whisper)
        else:
            # # add whisper by port param
            whisper = WhisperService()
            whisper.ip = ip
            whisper.port = port
            whisper_list.append(whisper)

        self.service_manager.updateWhisper(storage_server, whisper_list)
        self.debug("[%08X] <storage_server_sync> %d whisper found from '%s'" %
              (session.session_id, len(whisper_list), storage_server))
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        request = session.initial_message
        storage_server = request.getString(ParamKeyDefine.target)
        self.warn("[%08X] <storage_server_sync> query whisper fail, target '%s'" %
                  (session.session_id, storage_server))
        session.finish()

    def onTimeout(self, msg, session):
        request = session.initial_message
        storage_server = request.getString(ParamKeyDefine.target)
        self.warn("[%08X] <storage_server_sync> query whisper timeout, target '%s'" %
                  (session.session_id, storage_server))
        session.finish()

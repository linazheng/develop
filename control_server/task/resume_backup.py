#!/usr/bin/python
from host_info import BackupHostModeEnum
from host_info import EnableLocalBackupEnum
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class ResumeBackupTask(BaseTask):
    
    timeout = 60
    
    def __init__(self, task_type, message_handler, config_manager):
        logger_name = "task.resume_backup"
        self.config_manager = config_manager
        BaseTask.__init__(self, task_type, RequestDefine.resume_host, message_handler, logger_name)
        
        state_operate = 1
        self.addState(state_operate)
        
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.ack, result_success, self.onAck, state_operate)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.resume_host, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.resume_host, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)
        
        self.addTransferRule(state_operate, AppMessage.EVENT, EventDefine.report, result_success, self.onReport, state_operate)
        self.addTransferRule(state_operate, AppMessage.RESPONSE, RequestDefine.resume_host, result_fail, self.onFail)
        self.addTransferRule(state_operate, AppMessage.RESPONSE, RequestDefine.resume_host, result_success, self.onSuccess)
        self.addTransferRule(state_operate, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)
        
    def invokeSession(self, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        mode = request.getUInt(ParamKeyDefine.mode)
        disk = request.getUInt(ParamKeyDefine.disk)

        self.info("[%08X]receive resume host backup request, uuid '%s', mode '%d', disk '%d'" %
                  (session.session_id, uuid, mode, disk))

        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]resume host backup fail, host '%s' does not exist" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return

        host_info = self.config_manager.getHost(uuid)

        if mode not in (BackupHostModeEnum.fully, BackupHostModeEnum.partial):
            self.error("[%08X]resume host backup fail, no support mode '%d'" %
                       (session.session_id, mode))
            self.taskFail(session)
            return

#         if host_info.enable_local_backup != EnableLocalBackupEnum.enabled:
#             self.error("[%08X]resume host backup fail, host '%s' does not support backup" %
#                        (session.session_id, uuid))
#             self.taskFail(session)
#             return
        
        request.setUInt(ParamKeyDefine.disk_type, host_info.disk_type)
        request.session = session.session_id
        self.sendMessage(request, host_info.container)
        
        self.setTimer(session, self.timeout)
        
    def onAck(self, msg, session):
        self.clearTimer(session)
        
#         request = session.initial_message
#         uuid = request.getString(ParamKeyDefine.uuid)
#         self.info("[%08X]<resume_backup>resume host backup start, host id '%s'..." %
#                   (session.session_id, uuid))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        
        self.setTimer(session, self.timeout)
    
    def onFail(self, msg, session):
        self.clearTimer(session)
        
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        mode = request.getUInt(ParamKeyDefine.mode)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.error("[%08X]resume host backup fail, host '%s' in mode '%d' at disk %d'" %
                   (session.session_id, uuid, mode, disk))
        
        self.taskFail(session)
    
    def onSuccess(self, msg, session):
        self.clearTimer(session)
        
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        mode = request.getUInt(ParamKeyDefine.mode)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.info("[%08X]resume host backup success, host '%s' in mode '%d' at disk '%d'" %
                  (session.session_id, uuid, mode, disk))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        
        session.finish()
    
    def onTimeout(self, msg, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        mode = request.getUInt(ParamKeyDefine.mode)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.error("[%08X]resume host backup timeout, host '%s' in mode '%d' at disk '%d'" %
                   (session.session_id, uuid, mode, disk))
        
        self.taskFail(session)
    
    def onReport(self, msg, session):
        self.clearTimer(session)
        
#         request = session.initial_message
#         uuid = request.getString(ParamKeyDefine.uuid)
#         
#         level = msg.getUInt(ParamKeyDefine.level)
#         
#         self.debug("[%08X]<resume_backup>resume host '%s' backup at progress %d%%..." %
#                    (session.session_id, uuid, level))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        
        self.setTimer(session, self.timeout)
        
        
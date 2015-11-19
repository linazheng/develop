#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum
from compute_pool import ThinProvisioningModeEnum
from disk_image import DiskImageFileTypeEnum
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class FlushDiskImageTask(BaseTask):
    
    timeout = 60
    
    def __init__(self, task_type, message_handler, config_manager, image_manager):
        self.config_manager = config_manager
        self.image_manager = image_manager
        logger_name = "task.flush_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.flush_disk_image, message_handler, logger_name)
        
        #state rule define
        state_flush = 2
        self.addState(state_flush)
        
        #state_initial
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.ack, result_success, self.onStarted, state_flush)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.flush_disk_image, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.flush_disk_image, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)
        
        #state_flush
        self.addTransferRule(state_flush, AppMessage.EVENT, EventDefine.report, result_success, self.onReport, state_flush)
        self.addTransferRule(state_flush, AppMessage.RESPONSE, RequestDefine.flush_disk_image, result_success, self.onSuccess)
        self.addTransferRule(state_flush, AppMessage.RESPONSE, RequestDefine.flush_disk_image, result_fail, self.onFail)
        self.addTransferRule(state_flush, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)
        
    def invokeSession(self, session):
        request = session.initial_message
        
        uuid = request.getString(ParamKeyDefine.uuid)
        disk = request.getUInt(ParamKeyDefine.disk)
        mode = request.getUInt(ParamKeyDefine.mode)
        image_id = request.getString(ParamKeyDefine.image)
        
        self.info("[%08X] <flush_disk_image> receive request from '%s', host id '%s', disk index '%d'" %
                  (session.session_id, session.request_module, uuid, disk))
        
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X] <flush_disk_image> fail, host '%s' does not exist" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return
            
        host_info = self.config_manager.getHost(uuid)
        disk_type = host_info.disk_type
        service_name = host_info.container
        
        if mode != 0:
            self.error("[%08X] <flush_disk_image> fail, no support mode '%d'" %
                       (session.session_id, mode))
            self.taskFail(session)
            return
        
        if not self.image_manager.containsImage(image_id):
            self.error("[%08X] <flush_disk_image> fail, image '%s' does not exist" %
                       (session.session_id, image_id))
            self.taskFail(session)
            return
        
        image = self.image_manager.getImage(image_id)
        target = image.container
        
        if host_info.thin_provisioning == ThinProvisioningModeEnum.enabled:
            if image.file_type != DiskImageFileTypeEnum.qcow2:
                self.error("[%08X] <flush_disk_image> fail, host '%s' thin provisioning is enable, and image file type must be qcow2" %
                           (session.session_id, host_info.name))
                self.taskFail(session)
                return
        
        if disk_type == ComputeStorageTypeEnum.nas:
            request.setString(ParamKeyDefine.image, image.path)
        elif disk_type == ComputeStorageTypeEnum.local:
            request.setString(ParamKeyDefine.target, target)
        
        request.session = session.session_id
        request.setUInt(ParamKeyDefine.disk_type, disk_type)
        self.sendMessage(request, service_name)
        
        self.setTimer(session, self.timeout)
    
    def onStarted(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <flush_disk_image> started" %
                  session.session_id)
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        self.setTimer(session, self.timeout)
    
    def onSuccess(self, msg, session):
        self.clearTimer(session)
        
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.info("[%08X] <flush_disk_image> success, host '%s' at disk '%d'" %
                  (session.session_id, uuid, disk))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()
    
    def onFail(self, msg, session):
        self.clearTimer(session)
        
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.error("[%08X] <flush_disk_image> fail, host '%s' at disk '%d'" %
                  (session.session_id, uuid, disk))
        
        self.taskFail(session)
    
    def onTimeout(self, msg, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        disk = request.getUInt(ParamKeyDefine.disk)
        self.error("[%08X] <flush_disk_image> timeout, host '%s' at disk '%d'" %
                  (session.session_id, uuid, disk))
        
        self.taskFail(session)
        
    def onReport(self, msg, session):
        self.clearTimer(session)
        level = msg.getUInt(ParamKeyDefine.level)        
        self.info("[%08X] <flush_disk_image> flush disk image on progress %d%%..." %
                  (session.session_id, level))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        self.setTimer(session, self.timeout)
    
    
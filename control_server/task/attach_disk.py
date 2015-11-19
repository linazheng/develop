#!/usr/bin/python

from transaction.base_task import *
from service.message_define import *
from file_system_format_enum import FileSystemFormatEnum

class AttachDiskTask(BaseTask):
    
    operate_timeout = 10
    
    
    def __init__(self, task_type, messsage_handler, config_manager):
        self.config_manager = config_manager
        logger_name = "task.attach_disk"
        BaseTask.__init__(self, task_type, RequestDefine.attach_disk,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_disk, result_success,
                             self.onAttachSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.attach_disk, result_fail,
                             self.onAttachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAttachTimeout)        

    def invokeSession(self, session):
        
        request = session.initial_message
        uuid        = request.getString(ParamKeyDefine.uuid)
        disk_volume = request.getUInt(ParamKeyDefine.disk_volume)
        disk_type   = request.getUInt(ParamKeyDefine.disk_type)
        format_mode = request.getUInt(ParamKeyDefine.mode)
        
        self.info("[%08X]receive attach disk request from '%s', host id '%s', volume %.1f GB"%(
            session.session_id, 
            session.request_module,
            uuid, 
            float(disk_volume)/1073741824))
        
        if 0 != disk_type:
            self.error("[%08X]attach disk fail, disk type %d not supported"%(
                session.session_id, disk_type))
            self.taskFail(session)
            return
        
        
        if FileSystemFormatEnum.format_dict.has_key(format_mode)==False:
            self.error("[%08X]attach disk fail, disk format %d not supported"%(
                session.session_id, format_mode))
            self.taskFail(session)
            return
        
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]attach disk fail, invalid id '%s'"%(
                session.session_id, uuid))
            self.taskFail(session)
            return        
        
        
        ##get container
        host = self.config_manager.getHost(uuid)
        service_name = host.container
        
        self.info("[%08X]redirect attach disk '%s'('%s') to compute node '%s'"%(
            session.session_id, host.name, host.uuid, service_name))
        
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)


    def onAttachSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]attach disk success, id '%s'"%(
            session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()


    def onAttachFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]attach disk fail, id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)
        
        
    def onAttachTimeout(self, msg, session):
        self.error("[%08X]attach disk timeout, id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)


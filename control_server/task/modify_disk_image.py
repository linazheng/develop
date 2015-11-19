#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from disk_image import *

class ModifyDiskImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 disk_manager):
        self.disk_manager = disk_manager
        logger_name = "task.modify_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.modify_disk_image,
                          messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_disk_image, result_success,
                             self.onModifyDiskSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_disk_image, result_fail,
                             self.onModifyDiskFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyDiskTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        session.target = uuid
        if not self.disk_manager.containsImage(uuid):
            self.error("[%08X]modify disk image fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        image = self.disk_manager.getImage(uuid)
        service_node = image.container
        
        request.session = session.session_id
        self.info("[%08X]request modify disk images '%s' to '%s'..."%(
            session.session_id, image.name, service_node))
        
        self.sendMessage(request, service_node)
        self.setTimer(session, self.operate_timeout)        
        
    def onModifyDiskSuccess(self, response, session):
        self.clearTimer(session)
        request = session.initial_message
        uuid = session.target
        info = DiskImage()
        info.name = request.getString(ParamKeyDefine.name)
        info.description = request.getString(ParamKeyDefine.description)
        info.tags = request.getStringArray(ParamKeyDefine.identity)
        
        if not self.disk_manager.modifyImage(uuid, info):
            self.error("[%08X]modify disk image success, but can't modify image '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        
        self.info("[%08X]modify disk images success, image '%s' modified"%
                  (session.session_id, uuid))
        
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        
        session.finish()

    def onModifyDiskFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]modify disk images fail"%session.session_id)
        self.taskFail(session)

    def onModifyDiskTimeout(self, response, session):
        self.info("[%08X]modify disk images timeout"%session.session_id)
        self.taskFail(session)
        
    

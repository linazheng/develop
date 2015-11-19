#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from disk_image import *

class DeleteDiskImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 disk_manager):
        self.disk_manager = disk_manager
        logger_name = "task.delete_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.delete_disk_image,
                          messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_disk_image, result_success,
                             self.onDeleteDiskSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_disk_image, result_fail,
                             self.onDeleteDiskFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteDiskTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        session.target = uuid
        if not self.disk_manager.containsImage(uuid):
            self.error("[%08X]delete disk image fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        image = self.disk_manager.getImage(uuid)
        service_node = image.container
        
        request.session = session.session_id
        self.info("[%08X]request delete disk images '%s' to '%s'..."%(
            session.session_id, image.name, service_node))
        
        self.sendMessage(request, service_node)
        self.setTimer(session, self.operate_timeout)        
        
    def onDeleteDiskSuccess(self, response, session):
        self.clearTimer(session)
        uuid = session.target
        if not self.disk_manager.removeImage(uuid):
            self.error("[%08X]delete disk image success, but can't remove image '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        
        self.info("[%08X]delete disk images success, image '%s' removed"%
                  (session.session_id, uuid))
        
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        
        session.finish()

    def onDeleteDiskFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]delete disk images fail"%session.session_id)
        self.taskFail(session)

    def onDeleteDiskTimeout(self, response, session):
        self.info("[%08X]delete disk images timeout"%session.session_id)
        self.taskFail(session)
        
    

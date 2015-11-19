#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from iso_image import *

class DeleteISOImageTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 iso_manager):
        self.iso_manager = iso_manager
        logger_name = "task.delete_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.delete_iso_image,
                          messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_iso_image, result_success,
                             self.onDeleteISOSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_iso_image, result_fail,
                             self.onDeleteISOFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteISOTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        session.target = uuid
        if not self.iso_manager.containsImage(uuid):
            self.error("[%08X]delete iso image fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        image = self.iso_manager.getImage(uuid)
        service_node = image.container
        
        request.session = session.session_id
        self.info("[%08X]request delete iso images '%s' to '%s'..."%(
            session.session_id, image.name, service_node))
        
        self.sendMessage(request, service_node)
        self.setTimer(session, self.operate_timeout)        
        
    def onDeleteISOSuccess(self, response, session):
        self.clearTimer(session)
        uuid = session.target
        if not self.iso_manager.removeImage(uuid):
            self.error("[%08X]delete iso image success, but can't remove image '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        
        self.info("[%08X]delete iso images success, image '%s' removed"%
                  (session.session_id, uuid))
        
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        
        session.finish()

    def onDeleteISOFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]delete iso images fail"%session.session_id)
        self.taskFail(session)

    def onDeleteISOTimeout(self, response, session):
        self.info("[%08X]delete iso images timeout"%session.session_id)
        self.taskFail(session)
        
    

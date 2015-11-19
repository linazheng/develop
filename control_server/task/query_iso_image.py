#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from iso_image import *

class QueryISOImageTask(BaseTask):
    def __init__(self, task_type, messsage_handler, iso_manager):
        self.iso_manager = iso_manager
        logger_name = "task.query_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.query_iso_image,
                          messsage_handler, logger_name)
        
    def invokeSession(self, session):
        """
        task start, must override
        """
        image_list = self.iso_manager.getAllImages()
        
        response = getResponse(RequestDefine.query_iso_image)
        response.session = session.request_session
        response.success = True
        name = []
        uuid = []
        status = []
        size = []
        description = []
        if 0 != len(image_list):
            for image in image_list:
                name.append(image.name)
                uuid.append(image.uuid)
                if image.enabled:
                    status.append(0)
                else:
                    status.append(1)
                size.append(image.size)
                description.append(image.description)
                
        response.setStringArray(ParamKeyDefine.name, name)
        response.setStringArray(ParamKeyDefine.uuid, uuid)
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setUIntArray(ParamKeyDefine.size, size)
        response.setStringArray(ParamKeyDefine.description, description)
                  
        self.info("[%08X]query iso image success, %d image(s) available"%(
            session.session_id, len(image_list)))
        self.sendMessage(response, session.request_module)
        session.finish()

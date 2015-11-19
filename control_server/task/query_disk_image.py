#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from disk_image import *

class QueryDiskImageTask(BaseTask):
    def __init__(self, task_type, messsage_handler, image_manager):
        self.image_manager = image_manager
        logger_name = "task.query_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.query_disk_image,
                          messsage_handler, logger_name)
        
    def invokeSession(self, session):
        """
        task start, must override
        """
        image_list = self.image_manager.getAllImages()
        
        response = getResponse(RequestDefine.query_disk_image)
        response.session = session.request_session
        response.success = True
        name = []
        uuid = []
        status = []
        size = []
        description = []
        identity = []
        file_type = []
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
                identity.append(image.tags)
                file_type.append(image.file_type)
                
        response.setStringArray(ParamKeyDefine.name, name)
        response.setStringArray(ParamKeyDefine.uuid, uuid)
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setUIntArray(ParamKeyDefine.size, size)
        response.setStringArray(ParamKeyDefine.description, description)
        response.setStringArrayArray(ParamKeyDefine.identity, identity)
        response.setUIntArray(ParamKeyDefine.file_type, file_type)
                  
        self.info("[%08X]query disk image success, %d image(s) available"%(
            session.session_id, len(image_list)))
        self.sendMessage(response, session.request_module)
        session.finish()

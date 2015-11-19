#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from compute_resource import *

class RemoveComputeResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 compute_manager):
        self.compute_manager = compute_manager
        logger_name = "task.remove_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_compute_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.pool)
        name = request.getString(ParamKeyDefine.name)
        if not self.compute_manager.removeResource(uuid, [name]):
            self.error("[%08X]remove compute resource fail, name '%s'"%
                       (session.session_id, name))
            self.taskFail(session)
            return
        

        self.info("[%08X]remove compute resource success, name '%s'"%
                  (session.session_id, name))
        
        response = getResponse(RequestDefine.remove_compute_resource)
        response.session = session.request_session
        response.success = True
    
        self.sendMessage(response, session.request_module)
        session.finish()

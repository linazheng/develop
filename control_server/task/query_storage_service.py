#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from data.storage_config import *

class QueryStorageServicekTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 storage_manager):
        self.storage_manager = storage_manager
        logger_name = "task.query_storage_service"
        BaseTask.__init__(self, task_type, RequestDefine.query_storage_service,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        ##default storage service
        storage = self.storage_manager.getDefaultStorage()
        if not storage:
            self.error("[%08X]query storage service fail, no storage available"%
                       session.session_id)
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.query_storage_service)
        response.session = session.request_session
        response.success = True
        storage.toMessage(response)
        self.info("[%08X]query storage service success, storage '%s' available"%(
            session.session_id, storage.name))
        self.sendMessage(response, session.request_module)
        session.finish()

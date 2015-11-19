#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class QueryStoragePoolTask(BaseTask):
    
    query_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_manager):
        self.storage_manager = storage_manager
        logger_name = "task.query_storage_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_storage_pool, messsage_handler, logger_name)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_storage_pool, result_success,
                             self.onQuerySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_storage_pool, result_fail,
                             self.onQueryFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout, state_finish)
        

    def invokeSession(self, session):
        self.info("[%08X]receive query storage pool request from '%s'." % (session.session_id, session.request_module))
            
        _request = session.initial_message
        _request.session = session.session_id
        
        if not self.message_handler.sendToDefaultDataIndex(_request):
            self.taskFail(session)
            return 
            
        self.setTimer(session, self.query_timeout)

    
    def onQuerySuccess(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query storage pool success." % (session.session_id))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()


    def onQueryFail(self, response, session):
        self.clearTimer(session)
        self.error("[%08X]query storage pool fail." % (session.session_id))
        self.taskFail(session)
        
        
    def onQueryTimeout(self, response, session):
        self.clearTimer(session)
        self.error("[%08X]query storage pool timeout." % (session.session_id))
        self.taskFail(session)
        
        

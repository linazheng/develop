#!/usr/bin/python
# -*- coding: utf-8 -*-

from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class DeleteStoragePoolTask(BaseTask):
    
    delete_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.delete_storage_pool"
        BaseTask.__init__(self, task_type, RequestDefine.delete_storage_pool, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_storage_pool, result_success,
                             self.onDeleteSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.delete_storage_pool, result_fail,
                             self.onDeleteFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDeleteTimeout, state_finish)


    def invokeSession(self, session):
        
        self.info("[%08X]receive delete storage pool request from '%s'." % (session.session_id, session.request_module))
        
        session._ext_data = {}
        
        _request = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
        
        if not self.message_handler.sendToDefaultDataIndex(_request):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.delete_timeout)
        

    
    def onDeleteSuccess(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        if response.success==False:
            self.error("[%08X]delete storage pool fail." % session.session_id)
            return
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.storage_pool_manager.removeStoragePool(_uuid)
         
        self.info("[%08X]delete storage pool success, uuid '%s'." % (session.session_id, _uuid))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onDeleteFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.error("[%08X]delete storage pool fail, uuid '%s'." % (session.session_id, uuid))
        self.taskFail(session)
        
        
    def onDeleteTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.error("[%08X]delete storage pool timeout, uuid '%s'." % (session.session_id, uuid))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
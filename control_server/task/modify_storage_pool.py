#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class ModifyStoragePoolTask(BaseTask):
    
    modify_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.modify_storage_pool"
        BaseTask.__init__(self, task_type, RequestDefine.modify_storage_pool, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_storage_pool, result_success,
                             self.onModifySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.modify_storage_pool, result_fail,
                             self.onModifyFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onModifyTimeout, state_finish)


    def invokeSession(self, session):
        
        self.info("[%08X]receive modify storage pool request from '%s'." % (session.session_id, session.request_module))
        
        session._ext_data = {}
        
        _request = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
        
        if not self.message_handler.sendToDefaultDataIndex(_request):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.modify_timeout)
        

    
    def onModifySuccess(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        if response.success==False:
            self.error("[%08X]modify storage pool fail." % session.session_id)
            return
        
        uuid = _request.getString(ParamKeyDefine.uuid)
        name = _request.getString(ParamKeyDefine.name)
        
        _storagePool = self.storage_pool_manager.getStoragePool(uuid)
        if _storagePool:
            _storagePool.name = name
         
        self.info("[%08X]modify storage pool success, uuid '%s', name '%s'." % (session.session_id, uuid, name))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onModifyFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        uuid = _request.getString(ParamKeyDefine.uuid)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]modify storage pool fail, uuid '%s', name '%s'." % (session.session_id, uuid, name))
        self.taskFail(session)
        
        
    def onModifyTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        uuid = _request.getString(ParamKeyDefine.uuid)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]modify storage pool timeout, uuid '%s', name '%s'." % (session.session_id, uuid, name))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
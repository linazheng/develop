#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class RemoveStorageResourceTask(BaseTask):
    
    remove_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.remove_storage_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_storage_resource, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_storage_resource, result_success,
                             self.onRemoveSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_storage_resource, result_fail,
                             self.onRemoveFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout, state_finish)


    def invokeSession(self, session):
        
        self.info("[%08X]receive remove storage resource request from '%s'." % (session.session_id, session.request_module))
        
        session._ext_data = {}
        
        _request = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
        
        if not self.message_handler.sendToDefaultDataIndex(_request):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.remove_timeout)
        

    
    def onRemoveSuccess(self, response, session):
        self.clearTimer(session)
        
        _request           = session._ext_data["request"]
        
        if response.success==False:
            self.error("[%08X]remove storage resource fail." % session.session_id)
            return
        
        _pool = _request.getString(ParamKeyDefine.pool)
        _name = _request.getString(ParamKeyDefine.name)
        
        self.storage_pool_manager.removeStorageResource(_name)
         
        self.info("[%08X]remove storage resource success, pool '%s', name '%s'." % (session.session_id, _pool, _name))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onRemoveFail(self, response, session):
        self.clearTimer(session)
        
        _request           = session._ext_data["request"]
        
        pool = _request.getString(ParamKeyDefine.pool)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]remove storage resource fail, pool '%s', name '%s'." % (session.session_id, pool, name))
        self.taskFail(session)
        
        
    def onRemoveTimeout(self, response, session):
        self.clearTimer(session)
        
        _request           = session._ext_data["request"]
        
        pool = _request.getString(ParamKeyDefine.pool)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]remove storage resource timeout, pool '%s', name '%s'." % (session.session_id, pool, name))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
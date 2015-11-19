#!/usr/bin/python
# -*- coding: utf-8 -*-

from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class QueryDeviceTask(BaseTask):
    
    query_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        logger_name = "task.query_device"
        self.storage_pool_manager = storage_pool_manager
        BaseTask.__init__(self, task_type, RequestDefine.query_device, messsage_handler, logger_name)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_device, result_success,
                             self.onQuerySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_device, result_fail,
                             self.onQueryFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryTimeout, state_finish)
        

    def invokeSession(self, session):
        self.info("[%08X]receive query device request from '%s'." % (session.session_id, session.request_module))
            
        _request         = session.initial_message
        _request.session = session.session_id
        
        
        _type   = _request.getUInt(ParamKeyDefine.type);
        _target = _request.getString(ParamKeyDefine.target); 
        
        self.info("[%08X] receive query device request from '%s'." % (session.session_id, session.request_module))
    
        if _type!=0:
            self.error("[%08X] query device fail, only support type 0." % (session.session_id))
            self.taskFail(session)
            return
        if not _target:
            self.error("[%08X] query device fail, parameter 'pool' cannot be blank." % (session.session_id))
            self.taskFail(session)
            return
    
        _storagePool = self.storage_pool_manager.getStoragePool(_target)
        if _storagePool==None:
            self.error("[%08X] query device fail, storage pool not found, storage pool '%s'." % (session.session_id, _target))
            self.taskFail(session)
            return 
        if not _storagePool.data_index:
            self.error("[%08X] query device fail, target data_index not found, storage pool '%s'." % (session.session_id, _target))
            self.taskFail(session)
            return
        
        if not self.message_handler.sendMessage(_request, _storagePool.data_index):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.query_timeout)
        return
    
    
    def onQuerySuccess(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query device success." % (session.session_id))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        return


    def onQueryFail(self, response, session):
        self.clearTimer(session)
        self.error("[%08X]query device fail." % (session.session_id))
        self.taskFail(session)
        return 
        
        
    def onQueryTimeout(self, response, session):
        self.clearTimer(session)
        self.error("[%08X]query device timeout." % (session.session_id))
        self.taskFail(session)
        return
        
        

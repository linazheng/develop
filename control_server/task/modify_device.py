#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class ModifyDeviceTask(BaseTask):
    
    
    create_timeout = 10
    
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        logger_name = "task.modify_device"
        self.storage_pool_manager = storage_pool_manager
        BaseTask.__init__(self, task_type, RequestDefine.modify_device, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_device, result_success, self.onModifySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_device, result_fail,    self.onModifyFail,    state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onModifyTimeout, state_finish)



    def invokeSession(self, session):
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
               
        _uuid           = _request.getString(ParamKeyDefine.uuid);
        _name           = _request.getString(ParamKeyDefine.name);
        _option         = _request.getUIntArray(ParamKeyDefine.option);
        _user           = _request.getString(ParamKeyDefine.user);
        _authentication = _request.getString(ParamKeyDefine.authentication);
        _snapshot       = _request.getString(ParamKeyDefine.snapshot);
        
        self.info("[%08X] receive modify device request from '%s', name '%s'." % (session.session_id, session.request_module, _name))
        
        if not _uuid:
            self.error("[%08X] modify device '%s' fail, parameter 'uuid' cannot be blank." % (session.session_id, _uuid))
            self.taskFail(session)
            return ;
            
        _device = self.storage_pool_manager.getDevice(_uuid)
        if not _device:
            self.error("[%08X] modify device '%s' fail, device not found, device uuid '%s'." % (session.session_id, _name, _uuid))
            self.taskFail(session)
            return ;
        if not _device.storage_pool:
            self.error("[%08X] modify device '%s' fail, storage pool not found, storage pool '%s'." % (session.session_id, _name, _device.storage_pool))
            self.taskFail(session)
            return ;
    
        _storagePool = self.storage_pool_manager.getStoragePool(_device.storage_pool)
        if not _storagePool:
            self.error("[%08X] modify device '%s' fail, storage pool not found, storage pool '%s'." % (session.session_id, _name, _device.storage_pool))
            self.taskFail(session)
            return ;
        if not _storagePool.data_index:
            self.error("[%08X] modify device '%s' fail, target data_index not found, storage pool '%s'." % (session.session_id, _name, _device.storage_pool))
            self.taskFail(session)
            return ;
        
        if not self.message_handler.sendMessage(_request, _storagePool.data_index):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.create_timeout)
        return 

    
    def onModifySuccess(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _name = _request.getString(ParamKeyDefine.name)
        _uuid = response.getString(ParamKeyDefine.uuid)
         
        self.info("[%08X] modify device '%s' success, uuid '%s'." % (session.session_id, _name, _uuid))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onModifyFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        _name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X] modify device '%s' fail, uuid '%s'." % (session.session_id, _name, _uuid))
        self.taskFail(session)
        
        
    def onModifyTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        _name = _request.getString(ParamKeyDefine.name)
        
        _device = self.storage_pool_manager.getDevice(_uuid)
        if _device!=None:
            _device.name = _name
        
        self.error("[%08X] modify device '%s' timeout, uuid '%s'." % (session.session_id, _name, _uuid))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
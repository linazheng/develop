#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class DeleteDeviceTask(BaseTask):
    
    
    delete_timeout = 10
    
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        logger_name = "task.delete_device"
        self.storage_pool_manager = storage_pool_manager
        BaseTask.__init__(self, task_type, RequestDefine.delete_device, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.delete_device, result_success, self.onDeleteSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.delete_device, result_fail,    self.onDeleteFail,    state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onDeleteTimeout, state_finish)



    def invokeSession(self, session):
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
               
        _uuid           = _request.getString(ParamKeyDefine.uuid);
        
        self.info("[%08X] receive delete device request from '%s', uuid '%s'." % (session.session_id, session.request_module, _uuid))
        
        if not _uuid:
            self.error("[%08X] delete device fail, parameter 'uuid' cannot be blank." % (session.session_id))
            self.taskFail(session)
            return 
            
        _device = self.storage_pool_manager.getDevice(_uuid)
        if not _device:
            self.error("[%08X] delete device '%s' fail, device not found." % (session.session_id, _uuid))
            self.taskFail(session)
            return 
        if not _device.storage_pool:
            self.error("[%08X] delete device '%s' fail, storage pool not found, storage pool '%s'." % (session.session_id, _uuid, _device.storage_pool))
            self.taskFail(session)
            return 
    
        _storagePool = self.storage_pool_manager.getStoragePool(_device.storage_pool)
        if not _storagePool:
            self.error("[%08X] delete device '%s' fail, storage pool not found, storage pool '%s'." % (session.session_id, _uuid, _device.storage_pool))
            self.taskFail(session)
            return 
        if not _storagePool.data_index:
            self.error("[%08X] delete device '%s' fail, target data_index not found, storage pool '%s'." % (session.session_id, _uuid, _device.storage_pool))
            self.taskFail(session)
            return 
        
        if not self.message_handler.sendMessage(_request, _storagePool.data_index):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.delete_timeout)
        return

    
    def onDeleteSuccess(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.storage_pool_manager.deleteDevice(_uuid)
         
        self.info("[%08X] delete device '%s' success." % (session.session_id, _uuid))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onDeleteFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.error("[%08X] delete device '%s' fail." % (session.session_id, _uuid))
        self.taskFail(session)
        
        
    def onDeleteTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        _uuid = _request.getString(ParamKeyDefine.uuid)
        
        self.error("[%08X] delete device '%s' timeout." % (session.session_id, _uuid))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
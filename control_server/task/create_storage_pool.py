#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *

class CreateStoragePoolTask(BaseTask):
    
    create_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.create_storage_pool"
        BaseTask.__init__(self, task_type, RequestDefine.create_storage_pool, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_storage_pool, result_success,
                             self.onCreateSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_storage_pool, result_fail,
                             self.onCreateFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout, state_finish)


    def invokeSession(self, session):
        
        self.info("[%08X]receive create storage pool request from '%s'." % (session.session_id, session.request_module))
        
        session._ext_data = {}
        
        _request = session.initial_message
        _request.session = session.session_id
        
        _target_data_index = self.message_handler.getDefaultDataIndex()
        
        session._ext_data["request"]           = _request
        session._ext_data["target_data_index"] = _target_data_index
        
        # if not self.message_handler.sendToDefaultDataIndex(_request):
        if not self.message_handler.sendMessage(_request, _target_data_index):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.create_timeout)
        

    
    def onCreateSuccess(self, response, session):
        self.clearTimer(session)
        
        _request           = session._ext_data["request"]
        _target_data_index = session._ext_data["target_data_index"] 
        
        if response.success==False:
            self.error("[%08X]create storage pool fail." % session.session_id)
            return
        
        name = _request.getString(ParamKeyDefine.name)
        uuid = response.getString(ParamKeyDefine.uuid)
         
        self.info("[%08X]create storage pool success, name '%s', uuid '%s'." % (session.session_id, name, uuid))
        
        _storagePool = StoragePool()
        _storagePool.uuid         = uuid;
        _storagePool.name         = name;
#         _storagePool.node         = _nodeArr[i];
#         _storagePool.disk         = _diskArr[i];
#         _storagePool.cpu_count    = _cpuCountArr[i];
#         _storagePool.cpu_usage    = _cpuUsageArr[i];
#         _storagePool.memory       = _memoryArr[i];
#         _storagePool.memory_usage = _memoryUsageArr[i];
#         _storagePool.disk_volume  = _diskVolumeArr[i];
#         _storagePool.disk_usage   = _diskUsageArr[i];
#         _storagePool.status       = _statusArr[i];
        self.storage_pool_manager.addStoragePool(_target_data_index, _storagePool)
        
        
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onCreateFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        name = _request.getString(ParamKeyDefine.name)
        self.error("[%08X]create storage pool fail, name '%s'." % (session.session_id, name))
        self.taskFail(session)
        
        
    def onCreateTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        name = _request.getString(ParamKeyDefine.name)
        self.error("[%08X]create storage pool timeout, name '%s'." % (session.session_id, name))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
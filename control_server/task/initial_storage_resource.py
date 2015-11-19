#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from iso_image import *
from disk_image import *
from storage_resource import StorageResource

class InitialStorageResourceTask(BaseTask):
    
    
    
    query_timeout = 5
    
    
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.initial_storage_resource"
        BaseTask.__init__(self, task_type, RequestDefine.invalid, messsage_handler, logger_name)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_resource, result_success, self.onQuerySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_resource, result_fail,    self.onQueryFail,    state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,                  result_any,     self.onQueryTimeout, state_finish)
        
        

    def invokeSession(self, session):
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.id      = RequestDefine.query_storage_resource
        _request.session = session.session_id
        
        _target_data_index = _request.getString(ParamKeyDefine.server)
        _storage_pool_uuid = _request.getString(ParamKeyDefine.pool)
        
        
        session._ext_data["request"]           = _request
        session._ext_data["target_data_index"] = _target_data_index
        session._ext_data["storage_pool_uuid"] = _storage_pool_uuid
        
        self.info("[%08X] <initial_storage_resource> start to initialize storage resource info from '%s'." % (session.session_id, _target_data_index))
        
        if not _target_data_index:
            self.taskFail(session)
            return 
            
        self.message_handler.sendMessage(_request, _target_data_index)
        self.setTimer(session, self.query_timeout)
           
           
    
    def onQuerySuccess(self, response, session):
        self.clearTimer(session)
        
        _target_data_index = session._ext_data["target_data_index"]
        _storage_pool_uuid = session._ext_data["storage_pool_uuid"]
        
        self.info("[%08X] <initial_storage_resource> query storage resource success from '%s'." % (session.session_id, _target_data_index))
        
        _nameArr        = response.getStringArray(ParamKeyDefine.name);
        _statusArr      = response.getUIntArray(ParamKeyDefine.status);
        _cpuCountArr    = response.getUIntArray(ParamKeyDefine.cpu_count);
        _cpuUsageArr    = response.getFloatArray(ParamKeyDefine.cpu_usage);
        _memoryArr      = response.getUIntArrayArray(ParamKeyDefine.memory);
        _memoryUsageArr = response.getFloatArray(ParamKeyDefine.memory_usage);
        _diskVolumeArr  = response.getUIntArrayArray(ParamKeyDefine.disk_volume);
        _diskUsageArr   = response.getFloatArray(ParamKeyDefine.disk_usage);
        _ipArr          = response.getStringArray(ParamKeyDefine.ip);
        
        for i in xrange(len(_nameArr)):
            _storageResource = StorageResource()
            _storageResource.name         = _nameArr[i];
            _storageResource.status       = _statusArr[i];
            _storageResource.cpu_count    = _cpuCountArr[i];
            _storageResource.cpu_usage    = _cpuUsageArr[i];
            _storageResource.memory       = _memoryArr[i];
            _storageResource.memory_usage = _memoryUsageArr[i];
            _storageResource.disk_volume  = _diskVolumeArr[i];
            _storageResource.disk_usage   = _diskUsageArr[i];
            _storageResource.ip           = _ipArr[i];
            self.storage_pool_manager.addStorageResource(_storage_pool_uuid, _storageResource)
        
        session.finish()
        
        
    def onQueryFail(self, response, session):
        self.clearTimer(session)
        self.warn("[%08X] <initial_storage_resource> query storage resource fail." % (session.session_id))
        self.taskFail(session)
        
        
    def onQueryTimeout(self, response, session):
        self.clearTimer(session)
        self.error("[%08X] <initial_storage_resource> query storage resource timeout." % (session.session_id))
        self.taskFail(session)
        
        
        
        
        
        
        
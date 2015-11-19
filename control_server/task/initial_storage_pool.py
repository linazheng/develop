#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from iso_image import *
from disk_image import *
from storage_pool import StoragePool
from task.task_type import initial_storage_resource
from task.task_type import initial_device

class InitialStoragePoolTask(BaseTask):
    
    
    
    query_timeout = 5
    
    
    
    def __init__(self, task_type, messsage_handler, control_trans_manager, storage_pool_manager):
        
        self.control_trans_manager = control_trans_manager
        self.storage_pool_manager = storage_pool_manager
        
        logger_name = "task.initial_storage_pool"
        BaseTask.__init__(self, task_type, RequestDefine.invalid, messsage_handler, logger_name)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_pool, result_success, self.onQuerySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_storage_pool, result_fail,    self.onQueryFail,    state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,              result_any,     self.onQueryTimeout, state_finish)
        
              

    def invokeSession(self, session):
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.id      = RequestDefine.query_storage_pool
        _request.session = session.session_id
        
        _target_data_index = _request.getString(ParamKeyDefine.target)
        
        
        session._ext_data["request"]           = _request
        session._ext_data["target_data_index"] = _target_data_index
        
        
        self.info("[%08X] <initial_storage_pool> start to initialize storage pool info from '%s'." % (session.session_id, _target_data_index))
        
        if not _target_data_index:
            self.taskFail(session)
            return 
            
        self.message_handler.sendMessage(_request, _target_data_index)
        self.setTimer(session, self.query_timeout)
           
           
    
    def onQuerySuccess(self, response, session):
        self.clearTimer(session)
        
        _target_data_index = session._ext_data["target_data_index"]
        
        self.info("[%08X] <initial_storage_pool> query storage pool success from '%s'." % (session.session_id, _target_data_index))
        
        _uuidArr        = response.getStringArray(ParamKeyDefine.uuid);
        _nameArr        = response.getStringArray(ParamKeyDefine.name);
        _nodeArr        = response.getUIntArrayArray(ParamKeyDefine.node);
        _diskArr        = response.getUIntArrayArray(ParamKeyDefine.disk);
        _cpuCountArr    = response.getUIntArray(ParamKeyDefine.cpu_count);
        _cpuUsageArr    = response.getFloatArray(ParamKeyDefine.cpu_usage);
        _memoryArr      = response.getUIntArrayArray(ParamKeyDefine.memory);
        _memoryUsageArr = response.getFloatArray(ParamKeyDefine.memory_usage);
        _diskVolumeArr  = response.getUIntArrayArray(ParamKeyDefine.disk_volume);
        _diskUsageArr   = response.getFloatArray(ParamKeyDefine.disk_usage);
        _statusArr      = response.getUIntArray(ParamKeyDefine.status);
        
        for i in xrange(len(_uuidArr)):
            _storagePool = StoragePool()
            _storagePool.uuid         = _uuidArr[i];
            _storagePool.name         = _nameArr[i];
            _storagePool.node         = _nodeArr[i];
            _storagePool.disk         = _diskArr[i];
            _storagePool.cpu_count    = _cpuCountArr[i];
            _storagePool.cpu_usage    = _cpuUsageArr[i];
            _storagePool.memory       = _memoryArr[i];
            _storagePool.memory_usage = _memoryUsageArr[i];
            _storagePool.disk_volume  = _diskVolumeArr[i];
            _storagePool.disk_usage   = _diskUsageArr[i];
            _storagePool.status       = _statusArr[i];
            self.storage_pool_manager.addStoragePool(_target_data_index, _storagePool)
            
            # initialize storage resource
            _initial_storage_resource_session_id = self.control_trans_manager.allocTransaction(initial_storage_resource)
            _initial_storage_resource_request = getRequest(RequestDefine.invalid)
            _initial_storage_resource_request.setString(ParamKeyDefine.server, _target_data_index)
            _initial_storage_resource_request.setString(ParamKeyDefine.pool,   _storagePool.uuid)
            self.control_trans_manager.startTransaction(_initial_storage_resource_session_id, _initial_storage_resource_request)
            
            # initialize device
            _initial_device_session_id = self.control_trans_manager.allocTransaction(initial_device)
            _initial_device_request = getRequest(RequestDefine.invalid)
            _initial_device_request.setString(ParamKeyDefine.server, _target_data_index)
            _initial_device_request.setUInt(ParamKeyDefine.type,     0)
            _initial_device_request.setString(ParamKeyDefine.target, _storagePool.uuid)
            self.control_trans_manager.startTransaction(_initial_device_session_id, _initial_device_request)
               
        session.finish()
        
        
    def onQueryFail(self, response, session):
        self.clearTimer(session)
        self.warn("[%08X] <initial_storage_pool> query storage pool fail." % (session.session_id))
        self.taskFail(session)
        
        
    def onQueryTimeout(self, response, session):
        self.clearTimer(session)
        self.error("[%08X] <initial_storage_pool> query storage pool timeout." % (session.session_id))
        self.taskFail(session)
        
        
        
        
        
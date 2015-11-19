#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from iso_image import *
from disk_image import *
from storage_resource import StorageResource
from device import Device

class InitialDeviceTask(BaseTask):
    
    
    
    query_timeout = 5
    
    
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.initial_device"
        BaseTask.__init__(self, task_type, RequestDefine.invalid, messsage_handler, logger_name)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_device, result_success, self.onQuerySuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_device, result_fail,    self.onQueryFail,    state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,        result_any,     self.onQueryTimeout, state_finish)
        
              
        

    def invokeSession(self, session):
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.id      = RequestDefine.query_device
        _request.session = session.session_id
        
        
        _target_data_index = _request.getString(ParamKeyDefine.server)
        _query_type        = _request.getString(ParamKeyDefine.type)
        _storage_pool_uuid = _request.getString(ParamKeyDefine.target)
        
        
        session._ext_data["request"]           = _request
        session._ext_data["target_data_index"] = _target_data_index
        session._ext_data["query_type"]        = _query_type
        session._ext_data["storage_pool_uuid"] = _storage_pool_uuid
        
        self.info("[%08X] <initial_device> start to initialize device info from '%s'." % (session.session_id, _target_data_index))
        
        if not _target_data_index:
            self.taskFail(session)
            return 
            
        self.message_handler.sendMessage(_request, _target_data_index)
        self.setTimer(session, self.query_timeout)
           
           
    
    def onQuerySuccess(self, response, session):
        self.clearTimer(session)
        
        _target_data_index = session._ext_data["target_data_index"]
        _storage_pool_uuid = session._ext_data["storage_pool_uuid"]
        
        self.info("[%08X] <initial_device> query device success from '%s'." % (session.session_id, _target_data_index))
        
        _count = response.getUInt(ParamKeyDefine.count);
        
        if _count>0:
        
            _uuidArr        = response.getStringArray(ParamKeyDefine.uuid);
            _nameArr        = response.getStringArray(ParamKeyDefine.name);
            _statusArr      = response.getUIntArray(ParamKeyDefine.status);
            _diskVolumeArr  = response.getUIntArrayArray(ParamKeyDefine.disk_volume);
            _levelArr       = response.getUIntArray(ParamKeyDefine.level);
            _identityArr    = response.getStringArray(ParamKeyDefine.identity);
            _securityArr    = response.getUIntArray(ParamKeyDefine.security);
            _cryptArr       = response.getUIntArray(ParamKeyDefine.crypt);
            _pageArr        = response.getUIntArray(ParamKeyDefine.page);
            
            for i in xrange(len(_uuidArr)):
                _device = Device()
                _device.uuid        = _uuidArr[i];
                _device.name        = _nameArr[i];
                _device.status      = _statusArr[i];
                _device.disk_volume = _diskVolumeArr[i];
                _device.level       = _levelArr[i];
                _device.identity    = _identityArr[i];
                _device.security    = _securityArr[i];
                _device.crypt       = _cryptArr[i];
                _device.page        = _pageArr[i];
                self.storage_pool_manager.addDevice(_storage_pool_uuid, _device)
        
        session.finish()
        
        
    def onQueryFail(self, response, session):
        self.clearTimer(session)
        self.warn("[%08X] <initial_device> query device fail." % (session.session_id))
        self.taskFail(session)
        
        
    def onQueryTimeout(self, response, session):
        self.clearTimer(session)
        self.error("[%08X] <initial_device> query device timeout." % (session.session_id))
        self.taskFail(session)
        
        
        
        
        
        
        
#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *
from storage_pool_manager import StoragePoolManager
from device import Device

class CreateDeviceTask(BaseTask):
    
    create_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        logger_name = "task.create_device"
        self.storage_pool_manager = storage_pool_manager
        BaseTask.__init__(self, task_type, RequestDefine.create_device, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_device, result_success,
                             self.onCreateSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_device, result_fail,
                             self.onCreateFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout, state_finish)


    def invokeSession(self, session):
        
        
        session._ext_data = {}
        
        _request         = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
               
        _name           = _request.getString(ParamKeyDefine.name);
        _pool           = _request.getString(ParamKeyDefine.pool); 
#         _disk_volume    = _request.getUInt(ParamKeyDefine.disk_volume);
#         _page           = _request.getUInt(ParamKeyDefine.page);
#         _replication    = _request.getUInt(ParamKeyDefine.replication);
#         _option         = _request.getUIntArray(ParamKeyDefine.option);
#         _disk_type      = _request.getUIntArray(ParamKeyDefine.disk_type);
#         _user           = _request.getString(ParamKeyDefine.user);
#         _authentication = _request.getString(ParamKeyDefine.authentication);
#         _crypt          = _request.getString(ParamKeyDefine.crypt);
#         _snapshot       = _request.getString(ParamKeyDefine.snapshot);
        
        
        self.info("[%08X] receive create device request from '%s', name '%s'." % (session.session_id, session.request_module, _name))
    
        if not _pool:
            self.error("[%08X] create device '%s' fail, parameter 'pool' cannot be blank." % (session.session_id, _name))
            self.taskFail(session)
            return
    
        _storagePool = self.storage_pool_manager.getStoragePool(_pool)
        if not _storagePool:
            self.error("[%08X] create device '%s' fail, storage pool not found, storage pool '%s'." % (session.session_id, _name, _pool))
            self.taskFail(session)
            return
        if not _storagePool.data_index:
            self.error("[%08X] create device '%s' fail, target data_index not found, storage pool '%s'." % (session.session_id, _name, _pool))
            self.taskFail(session)
            return
        
        session._ext_data["storage_pool"] = _storagePool
        
        if not self.message_handler.sendMessage(_request, _storagePool.data_index):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.create_timeout)
        

    
    def onCreateSuccess(self, response, session):
        self.clearTimer(session)
        
        _request     = session._ext_data["request"]
        _storagePool = session._ext_data["storage_pool"]
        
        _uuid = response.getString(ParamKeyDefine.uuid)
        _name = _request.getString(ParamKeyDefine.name)
        
        _device = Device()
        _device.uuid        = _uuid;
        _device.name        = _name;
#         _device.status      = _statusArr[i];
#         _device.disk_volume = _diskVolumeArr[i];
#         _device.level       = _levelArr[i];
#         _device.identity    = _identityArr[i];
#         _device.security    = _securityArr[i];
#         _device.crypt       = _cryptArr[i];
#         _device.page        = _pageArr[i];
        self.storage_pool_manager.addDevice(_storagePool.uuid, _device)
         
        self.info("[%08X] create device '%s' success, uuid '%s'." % (session.session_id, _name, _uuid))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onCreateFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X] create device '%s' fail." % (session.session_id, name))
        self.taskFail(session)
        
        
    def onCreateTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X] create device '%s' timeout." % (session.session_id, name))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
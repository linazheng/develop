#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from storage_pool import *
from storage_resource import StorageResource

class AddStorageResourceTask(BaseTask):
    
    add_timeout = 10
    
    def __init__(self, task_type, messsage_handler, storage_pool_manager):
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.add_storage_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_storage_resource, messsage_handler, logger_name)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_storage_resource, result_success,
                             self.onAddSuccess, state_finish)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_storage_resource, result_fail,
                             self.onAddFail, state_finish)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout, state_finish)


    def invokeSession(self, session):
        
        self.info("[%08X]receive add storage resource request from '%s'." % (session.session_id, session.request_module))
        
        session._ext_data = {}
        
        _request = session.initial_message
        _request.session = session.session_id
        
        session._ext_data["request"] = _request
        
        if not self.message_handler.sendToDefaultDataIndex(_request):
            self.taskFail(session)
            return 
        
        self.setTimer(session, self.add_timeout)
        

    
    def onAddSuccess(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        if response.success==False:
            self.error("[%08X]add storage resource fail." % session.session_id)
            return
        
        _pool = _request.getString(ParamKeyDefine.pool)
        _name = _request.getString(ParamKeyDefine.name)
        
        _storageResource = StorageResource()
        _storageResource.name         = _name;
#         _storageResource.status       = _statusArr[i];
#         _storageResource.cpu_count    = _cpuCountArr[i];
#         _storageResource.cpu_usage    = _cpuUsageArr[i];
#         _storageResource.memory       = _memoryArr[i];
#         _storageResource.memory_usage = _memoryUsageArr[i];
#         _storageResource.disk_volume  = _diskVolumeArr[i];
#         _storageResource.disk_usage   = _diskUsageArr[i];
#         _storageResource.ip           = _ipArr[i];
        self.storage_pool_manager.addStorageResource(_pool, _storageResource)
         
        self.info("[%08X]add storage resource success, pool '%s', name '%s'." % (session.session_id, _pool, _name))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onAddFail(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        pool = _request.getString(ParamKeyDefine.pool)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]add storage resource fail, pool '%s', name '%s'." % (session.session_id, pool, name))
        self.taskFail(session)
        
        
    def onAddTimeout(self, response, session):
        self.clearTimer(session)
        
        _request = session._ext_data["request"]
        
        pool = _request.getString(ParamKeyDefine.pool)
        name = _request.getString(ParamKeyDefine.name)
        
        self.error("[%08X]add storage resource timeout, pool '%s', name '%s'." % (session.session_id, pool, name))
        self.taskFail(session)
        
        
        
        
        
        
        
        
        
        
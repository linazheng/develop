#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse



class NetworkAttachAddressTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager, address_manager):
        self.network_manager    = network_manager
        self.address_manager    = address_manager
        logger_name = "task.network_attach_address"
        BaseTask.__init__(self, task_type, RequestDefine.network_attach_address, messsage_handler, logger_name)

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"]        = request.getString(ParamKeyDefine.uuid)
        _parameter["count"]       = request.getUInt(ParamKeyDefine.count)
        
        self.info("[%08X] <network_attach_address> receive network attach address request from '%s', parameter: %s" % (session.session_id, 
                                                                                                                       session.request_module, 
                                                                                                                       _parameter))
        
        self.info("[%08X] <network_attach_address> network attach address success, network '%s', count '%s'" % (session.session_id, _parameter["uuid"], _parameter["count"]))
        
        # NetworkInfo
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <network_attach_address> network attach address fail, invalid network id '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        # allocate public ip
        _ipArr = []
        if _parameter["count"]>0:
            _ipArr = self._allocatePublicIps(_networkInfo.pool, _parameter["count"])
            
            if len(_ipArr) < _parameter["count"]:
                self.error("[%08X] <network_attach_address> network attach address fail, can't allocate public ip in address pool '%s'" % (session.session_id, _networkInfo.pool))
                self._deallocatePublicIps(_networkInfo.pool, _ipArr)
                self.taskFail(session)
                return
            
            self.network_manager.attachAddress(_networkInfo.uuid, _ipArr)
                
        # return 
        response = getResponse(RequestDefine.network_attach_address)
        response.session = session.request_session
        
        response.success = True
        
        response.setStringArray(ParamKeyDefine.ip, _ipArr)    
        
        self.sendMessage(response, session.request_module)
        session.finish()


    def _allocatePublicIps(self, address_pool_id, count):
        _ips = []
        for i in xrange(count):
            _ip = self.address_manager.allocate(address_pool_id)
            if _ip==None:
                return _ips
            _ips.append(_ip)
        return _ips
        
        
    def _deallocatePublicIps(self, address_pool_id, ips):
        for ip in ips:
            self.address_manager.deallocate(address_pool_id, ip)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


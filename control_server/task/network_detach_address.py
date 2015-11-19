#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse



class NetworkDetachAddressTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager, address_manager):
        self.network_manager    = network_manager
        self.address_manager    = address_manager
        logger_name = "task.network_detach_address"
        BaseTask.__init__(self, task_type, RequestDefine.network_detach_address, messsage_handler, logger_name)

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"] = request.getString(ParamKeyDefine.uuid)
        _parameter["ip"]   = request.getStringArray(ParamKeyDefine.ip)
        
        self.info("[%08X] <network_detach_address> receive network detach address request from '%s', parameter: %s" % (session.session_id, 
                                                                                                                       session.request_module, 
                                                                                                                       _parameter))
        
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <network_detach_address> network detach address fail, invalid network id '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        _deallocated_ips = []
        _undeallocated_ips = []
        for _ip in _parameter["ip"]:
            if _ip not in _networkInfo.public_ips:
                _undeallocated_ips.append(_ip)
                self.info("[%08X] <network_detach_address> network detach address fail, public ip '%s' isn't allocated to network '%s'" % (session.session_id, _parameter["ip"], _parameter["uuid"]))
                continue
            
            if self._isPublicIpBoundToHost(_networkInfo, _ip):
                _undeallocated_ips.append(_ip)
                self.info("[%08X] <network_detach_address> network detach address fail, public ip '%s' is bound to host, couldn't be detached from netwrok." % (session.session_id, _parameter["ip"]))
                continue
            
            if self.address_manager.deallocate(_networkInfo.pool, _ip):
                _deallocated_ips.append(_ip)
            else:
                _undeallocated_ips.append(_ip)
                
        self.network_manager.detachAddress(_networkInfo.uuid, _deallocated_ips)
        
        self.info("[%08X] <network_detach_address> network detach address success, network '%s', ip '%s'" % (session.session_id, _parameter["uuid"], _parameter["ip"]))
        
        # return 
        response = getResponse(RequestDefine.network_detach_address)
        response.session = session.request_session
        response.success = True
        
        response.setStringArrayArray(ParamKeyDefine.ip, [_deallocated_ips, _undeallocated_ips])    
        
        self.sendMessage(response, session.request_module)
        session.finish()

        
    def _isPublicIpBoundToHost(self, networkInfo, public_ip):
        for _bound_key, _bound_value in networkInfo.bound_ports.items():
            _bound_port_arr = _bound_key.split(":")
            _public_ip      = _bound_port_arr[1]
            if _public_ip==public_ip:
                return True
        return False
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


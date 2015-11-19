#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse
from network_info import NetworkInfo, NetworkStatus
from service import socket_util


class CreateNetworkTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager, address_manager):
        self.network_manager    = network_manager
        self.address_manager    = address_manager
        logger_name = "task.create_network"
        BaseTask.__init__(self, task_type, RequestDefine.create_network, messsage_handler, logger_name)

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["name"]        = request.getString(ParamKeyDefine.name)
        _parameter["netmask"]     = request.getUInt(ParamKeyDefine.netmask)
        _parameter["description"] = request.getString(ParamKeyDefine.description)
        _parameter["pool"]        = request.getString(ParamKeyDefine.pool)              # address pool uuid
        
        self.info("[%08X] <create_network> receive create network request from '%s', parameter: %s" % (session.session_id, 
                                                                                                       session.request_module, 
                                                                                                       _parameter))
        
        _networkInfo = NetworkInfo()
        _networkInfo.name        = _parameter["name"]
        _networkInfo.netmask     = _parameter["netmask"]
        _networkInfo.description = _parameter["description"]
        _networkInfo.pool        = _parameter["pool"]
        _networkInfo.status      = NetworkStatus.enabled
        
        if not self.address_manager.containsPool(_networkInfo.pool):
            self.error("[%08X] <create_network> create network fail, invalid address pool id '%s'" % (session.session_id, _networkInfo.pool))
            self.taskFail(session)
            return
        
        if _networkInfo.netmask!=27:
            self.error("[%08X] <create_network> create network fail, wrong value of parameter netmask '%s', can only be 27" % (session.session_id, _networkInfo.netmask))
            self.taskFail(session)
            return
        
        if _networkInfo.netmask<9 or _networkInfo.netmask>=32:
            self.error("[%08X] <create_network> create network fail, wrong value of parameter netmask '%s', can only between 9 and 31" % (session.session_id, _networkInfo.netmask))
            self.taskFail(session)
            return
        
        _networkInfo.size = socket_util.convertNetmaskToSize(_networkInfo.netmask);
        
        if not self.network_manager.createNetwork(_networkInfo):
            self.error("[%08X] <create_network> create network fail, name '%s'" % (session.session_id, _networkInfo.name))
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.create_network)
        response.session = session.request_session
        response.success = True
        
        response.setString(ParamKeyDefine.uuid,            _networkInfo.uuid)
        response.setString(ParamKeyDefine.network_address, _networkInfo.network_address)
                
        self.sendMessage(response, session.request_module)
        session.finish()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


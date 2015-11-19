#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class GetForwarderTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, forwarder_manager):
        self.forwarder_manager = forwarder_manager
        logger_name = "task.get_forwarder"
        BaseTask.__init__(self, task_type, RequestDefine.get_forwarder, messsage_handler, logger_name)
    
    
    def invokeSession(self, session):
        """
        task start, must override
        """
        forwarder_id = session.initial_message.getString(ParamKeyDefine.uuid)
        self.info("[%08X] <get_forwarder> receive get forwarder request from '%s', forwarder id '%s'"%(session.session_id, session.request_module, forwarder_id))

        if not self.forwarder_manager.contains(forwarder_id):
            self.error("[%08X] <get_forwarder> get forwarder fail, invalid id '%s'"%(session.session_id, forwarder_id))
            self.taskFail(session)
            return
        
        forwarder = self.forwarder_manager.get(forwarder_id)
        
        _address = ""
        _netmask = "0"
        if forwarder.vpc_range:
            _address, _netmask = forwarder.vpc_range.split("/")
        
        
        response = getResponse(RequestDefine.get_forwarder)
        response.session = session.request_session
        response.success = True
 
        response.setUInt(ParamKeyDefine.type,   forwarder.type)
        response.setString(ParamKeyDefine.uuid, forwarder.host_id)                
        response.setString(ParamKeyDefine.name, forwarder.host_name)         
        response.setUInt(ParamKeyDefine.status, 1 if (forwarder.enable==True) else 0)
        
        response.setString(ParamKeyDefine.network_address, forwarder.vpc_ip)             # response.setString(ParamKeyDefine.vpc_ip, forwarder.vpc_ip)
        response.setString(ParamKeyDefine.address,         _address)                     # response.setString(ParamKeyDefine.vpc_range,       forwarder.vpc_range)
        response.setUInt(ParamKeyDefine.netmask,           int(_netmask))
        
        ip = [forwarder.server_ip]
        if 0 != len(forwarder.public_ip):
            ip.extend(forwarder.public_ip)
            
        response.setStringArray(ParamKeyDefine.ip, ip)                
        response.setUIntArray(ParamKeyDefine.display_port,
                              [forwarder.server_monitor, forwarder.public_monitor])
        port = []
        target = []
        if 0 != len(forwarder.port):
            for forwarder_port in forwarder.port:
                port.extend([forwarder_port.protocol,
                             forwarder_port.host_port,
                             forwarder_port.server_port,
                             forwarder_port.public_port])
                target.append(forwarder_port.public_ip);
        response.setUIntArray(ParamKeyDefine.port, port)
        response.setStringArray(ParamKeyDefine.target, target)
            
        response.setUIntArray(ParamKeyDefine.range, forwarder.output_port_range)
        
        self.info("[%08X] <get_forwarder> get forwarder success, target host '%s'('%s')"%(session.session_id, forwarder.host_name, forwarder.host_id))
        self.sendMessage(response, session.request_module)
        session.finish()







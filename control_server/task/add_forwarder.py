#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from host_info import *
from host_forwarder import *

class AddForwarderTask(BaseTask):
    
    operate_timeout = 5
    
    def __init__(self, task_type, messsage_handler,
                 config_manager, compute_pool_manager,
                 address_manager, port_manager,
                 forwarder_manager):
        
        self.config_manager = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.address_manager = address_manager
        self.port_manager = port_manager
        self.forwarder_manager = forwarder_manager
        
        logger_name = "task.add_forwarder"
        
        BaseTask.__init__(self, task_type, RequestDefine.add_forwarder,
                          messsage_handler, logger_name)

        ##state rule define, state id from 1
        stAddForwarder = 2
        self.addState(stAddForwarder)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_forwarder, result_success,
                             self.onAttachSuccess, stAddForwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.add_forwarder, result_fail,
                             self.onAttachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAttachTimeout)
        
        # stAddForwarder
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE,
                             RequestDefine.add_forwarder, result_success,
                             self.onAddSuccess)
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE,
                             RequestDefine.add_forwarder, result_fail,
                             self.onAddFail)
        self.addTransferRule(stAddForwarder, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onAddTimeout)
        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        target_id = request.getString(ParamKeyDefine.target)
        target_type = request.getUInt(ParamKeyDefine.type)
        network_type = request.getUInt(ParamKeyDefine.network_type)        
        network_source = request.getString(ParamKeyDefine.network_source)
        
        self.info("[%08X]receive add forwarder request from '%s', target id '%s',type %d, network type %d, source '%s'"%(
                session.session_id, session.request_module, target_id, target_type,
                network_type, network_source))
        
        if 1 == target_type:
            ##disk
            self.error("[%08X]add forwarder fail, disk forwarder not supported"%(
                session.session_id))
            self.taskFail(session)
            return
        
        if NetworkTypeEnum.mono != network_type:
            self.error("[%08X]add forwarder fail, unsupport network type %d"%(
                session.session_id, network_type))
            self.taskFail(session)
            return
        
        ##check pool id
        if not self.address_manager.containsPool(network_source):
            self.error("[%08X]add forwarder fail, invalid address pool id '%s'"%(
                session.session_id, network_source))
            self.taskFail(session)
            return  
                  
        if not self.config_manager.containsHost(target_id):
            self.error("[%08X]add forwarder fail, invalid host id '%s'"%(
                session.session_id, target_id))
            self.taskFail(session)
            return
        
        ##check ir
        default_ir = self.message_handler.getDefaultIntelligentRouter()
        if default_ir is None:
            self.error("[%08X]add forwarder fail, no intelligent router actived"%(
                session.session_id))
            self.taskFail(session)
            return
            
        host = self.config_manager.getHost(target_id)
        public_ip = self.address_manager.allocate(network_source)
        if public_ip is None:
            self.error("[%08X]add forwarder fail, can't allocate ip in pool '%s'"%(
                session.session_id, network_source))
            self.taskFail(session)
            return
        
        forwarder = HostForwarder()
        forwarder.public_ip = [public_ip]
        forwarder.host_id = host.uuid
        forwarder.host_name = host.name
        forwarder.server_ip = host.server_ip
        forwarder.server_monitor = host.server_port
        forwarder.public_monitor = 5900
        
        if not self.forwarder_manager.create(forwarder):
            self.error("[%08X]add forwarder fail, can't create forwarder"%(
                session.session_id))
            self.address_manager.deallocate(network_source, public_ip)
            self.taskFail(session)
            return
        
        self.info("[%08X]host forwarder created, id '%s', from '%s:%d' to '%s:%d', target host '%s'('%s')"%(
                session.session_id, forwarder.uuid, public_ip, forwarder.public_monitor,
                forwarder.server_ip, forwarder.server_monitor, forwarder.host_name, forwarder.host_id))
        
        ##update host info
        host.public_ip = public_ip
        host.public_port = forwarder.public_monitor
        host.forwarder = forwarder.uuid
        host.network_type = network_type
        host.network_source = network_source

        new_request = getRequest(RequestDefine.add_forwarder)
        new_request.session = session.session_id
        new_request.setString(ParamKeyDefine.target,         target_id)
        new_request.setString(ParamKeyDefine.uuid,           forwarder.uuid)
        new_request.setUInt(ParamKeyDefine.network_type,     network_type)
        new_request.setString(ParamKeyDefine.network_source, network_source)
        new_request.setString(ParamKeyDefine.ip,             public_ip)
        new_request.setUInt(ParamKeyDefine.display_port,     forwarder.public_monitor)        
            
        self.sendMessage(new_request, host.container)
        self.setTimer(session, self.operate_timeout)
        session.target = forwarder.uuid
        
        self.info("[%08X]request add forwarder '%s' to compute node '%s'..."%(
            session.session_id, forwarder.uuid, host.container))

    def onAttachSuccess(self, msg, session):
        self.clearTimer(session)
        if not self.forwarder_manager.contains(session.target):
            self.error("[%08X]attach forwarder success, but forwarder '%s' not exists"%(
                session.session_id, session.target))
            self.taskFail(session)
            return
        ##check ir
        default_ir = self.message_handler.getDefaultIntelligentRouter()
        if default_ir is None:
            self.error("[%08X]attach forwarder success, but no intelligent router actived"%(
                session.session_id))
            self.taskFail(session)
            return
        forwarder = self.forwarder_manager.get(session.target)
        request = getRequest(RequestDefine.add_forwarder)
        request.session = session.session_id    
        request.setString(ParamKeyDefine.uuid, forwarder.uuid)
        request.setUInt(ParamKeyDefine.type, forwarder.type)
        request.setString(ParamKeyDefine.host, forwarder.host_id)
        request.setString(ParamKeyDefine.name, forwarder.host_name)
        ip = [forwarder.server_ip]
        ip.extend(forwarder.public_ip)
        request.setStringArray(ParamKeyDefine.ip, ip)
        request.setUIntArray(ParamKeyDefine.display_port, [forwarder.server_monitor, forwarder.public_monitor])
        port = []
        if 0 != len(forwarder.port):
            for forward_port in forwarder.port:
                port.extend([forward_port.server_port,
                             forward_port.public_port,
                             forward_port.host_port])
        request.setUIntArray(ParamKeyDefine.port, port)

        self.sendMessage(request, default_ir)
        self.setTimer(session, self.operate_timeout)

        self.info("[%08X]attach forwarder success, add forwarder to intelligent router '%s'..."%(
            session.session_id, default_ir))

    def onAttachFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]attach forwarder fail"%(
            session.session_id))
        if self.forwarder_manager.contains(session.target):
            forwarder = self.forwarder_manager.get(session.target)
            ##clear host info
            if self.config_manager.containsHost(forwarder.host_id):
                host = self.config_manager.getHost(forwarder.host_id)
                self.address_manager.deallocate(host.network_source, host.public_ip)
                host.public_ip = ""
                host.public_port = forwarder.public_monitor
                host.forwarder = ""
                self.info("[%08X]detach forwarder from host '%s'"%(
                    session.session_id, host.name))
            ##delete forwarder
            self.forwarder_manager.delete(session.target)
        self.taskFail(session)
        
    def onAttachTimeout(self, msg, session):
        self.error("[%08X]attach forwarder timeout"%(
            session.session_id))
        if self.forwarder_manager.contains(session.target):
            forwarder = self.forwarder_manager.get(session.target)
            ##clear host info
            if self.config_manager.containsHost(forwarder.host_id):
                host = self.config_manager.getHost(forwarder.host_id)
                self.address_manager.deallocate(host.network_source, host.public_ip)
                host.public_ip = ""
                host.public_port = forwarder.public_monitor
                host.forwarder = ""
                self.info("[%08X]detach forwarder from host '%s'"%(
                    session.session_id, host.name))
            ##delete forwarder
            self.forwarder_manager.delete(session.target)
        self.taskFail(session)
            
    def onAddSuccess(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]add forwarder to intelligent router success"%(
            session.session_id))
        forwarder_id = session.target
        response = getResponse(RequestDefine.add_forwarder)
        response.success = True
        response.session = session.request_session
        response.setString(ParamKeyDefine.uuid, forwarder_id)
        self.sendMessage(response, session.request_module)
        session.finish()
        
    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]add forwarder to intelligent router fail"%(
            session.session_id))
        if self.forwarder_manager.contains(session.target):
            forwarder = self.forwarder_manager.get(session.target)
            ##clear host info
            if self.config_manager.containsHost(forwarder.host_id):
                host = self.config_manager.getHost(forwarder.host_id)
                self.address_manager.deallocate(host.network_source, host.public_ip)
                host.public_ip = ""
                host.public_port = forwarder.public_monitor
                host.forwarder = ""
                self.info("[%08X]detach forwarder from host '%s'"%(
                    session.session_id, host.name))
            ##delete forwarder
            self.forwarder_manager.delete(session.target)
        self.taskFail(session)
        
    def onAddTimeout(self, msg, session):
        self.error("[%08X]add forwarder to intelligent router timeout"%(
            session.session_id))
        if self.forwarder_manager.contains(session.target):
            forwarder = self.forwarder_manager.get(session.target)
            ##clear host info
            if self.config_manager.containsHost(forwarder.host_id):
                host = self.config_manager.getHost(forwarder.host_id)
                self.address_manager.deallocate(host.network_source, host.public_ip)
                host.public_ip = ""
                host.public_port = forwarder.public_monitor
                host.forwarder = ""
                self.info("[%08X]detach forwarder from host '%s'"%(
                    session.session_id, host.name))
            ##delete forwarder
            self.forwarder_manager.delete(session.target)
        self.taskFail(session)
    

#!/usr/bin/python
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, EventDefine, getString,\
    ParamKeyDefine, getResponse, getRequest
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage
from compute_pool import ComputeNetworkTypeEnum

class DeleteHostTask(BaseTask):
    
    operate_timeout = 10
    
    def __init__(self, task_type, messsage_handler,
                 config_manager, compute_pool_manager,
                 address_manager, port_manager,
                 forwarder_manager, network_manager):
        
        self.config_manager       = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.address_manager      = address_manager
        self.port_manager         = port_manager
        self.forwarder_manager    = forwarder_manager
        self.network_manager      = network_manager
        logger_name = "task.delete_host"
        BaseTask.__init__(self, task_type, RequestDefine.delete_host, messsage_handler, logger_name)
        
        stRemoveForwarder = 2
        self.addState(stRemoveForwarder)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.delete_host, result_success, self.onDeleteSuccess, stRemoveForwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.delete_host, result_fail,    self.onDeleteFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,       result_any,     self.onDeleteTimeout)        

        # stRemoveForwarder
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveSuccess)
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail,    self.onRemoveFail)
        self.addTransferRule(stRemoveForwarder, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onRemoveTimeout)
        
        
    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        
        uuid = getString(request, ParamKeyDefine.uuid)
        
        self.info("[%08X] <delete_host> receive delete host '%s' request from '%s'" % (session.session_id, uuid, session.request_module))
        
        host = self.config_manager.getHost(uuid)
        if host==None:
            self.error("[%08X] <delete_host> delete host fail, invalid id '%s'" % (session.session_id, uuid))
            self.taskFail(session)
            return
        
        # detach host from vpc network
        if len(host.network)>0:
            
            _networkInfo = self.network_manager.getNetwork(host.network)
            
            if _networkInfo==None:
                
                self.warn("[%08X] <delete_host> network not found, invalid network uuid '%s'" % (session.session_id, host.network))
                
            else:
                # detash host 
                if not self.network_manager.detachHost(host.network, uuid, save=False):
                    self.warn("[%08X] <delete_host> detach host '%s' from network '%s' fail" % (session.session_id, uuid, host.network))
                else:
                    self.info("[%08X] <delete_host> detach host '%s' from network '%s' success" % (session.session_id, uuid, host.network))
                    
                # deallocate ip
                if not self.network_manager.deallocateIp(host.network, host.vpc_ip, save=False):
                    self.warn("[%08X] <delete_host> deallocate vpc ip '%s' from network '%s' fail" % (session.session_id, host.vpc_ip, host.network))
                else:
                    self.warn("[%08X] <delete_host> deallocate vpc ip '%s' from network '%s' success" % (session.session_id, host.vpc_ip, host.network))
                    
                # deallocate bind port
                for _host_port in host.port:
                    _key = "%s:%s:%s" % (_host_port.protocol, _host_port.public_ip, _host_port.public_port)
                    _networkInfo.bound_ports.pop(_key, None)
                    
                self.network_manager.saveNetworkInfo(host.network)
        else:
            self.info("[%08X] <delete_host> host '%s' does not attach to any vpc network" % (session.session_id, uuid))
        
        
        service_name = host.container
            
        self.info("[%08X] <delete_host> request delete host '%s'('%s') to compute node '%s'" % (session.session_id, host.name, host.uuid, service_name))
        
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)

    
    def onDeleteSuccess(self, msg, session):
        self.clearTimer(session)        
        
        if not self.config_manager.containsHost(session.target):
            self.error("[%08X] <delete_host> delete host success, but host '%s' not deleted" % (session.session_id, session.target))
            self.taskFail(session)
            return

        host = self.config_manager.getHost(session.target)
        
        #
        service_name = host.container        
        node_in_pool, pool_id = self.compute_pool_manager.searchResource(service_name)
        
        if node_in_pool:
            resource = self.compute_pool_manager.getResource(pool_id, service_name)
            ##remove from resource
            resource.removeHost(host.uuid)
            self.info("[%08X] <delete_host> remove host '%s' from compute resource '%s'" % (session.session_id, host.name, resource.name))
            ##save
            self.compute_pool_manager.savePoolResource(pool_id, resource.name)
            
        self.info("[%08X] <delete_host> delete host success, id '%s'"%(session.session_id, session.target))
        
        
        
        if ComputeNetworkTypeEnum.monopoly == host.network_type:
            
            if not bool(host.network):
                pool_id = host.network_source
                if not self.address_manager.deallocate(pool_id, host.public_ip):
                    self.warn("[%08X] <delete_host> deallocate public '%s' to address pool '%s' fail"%(session.session_id, host.public_ip, pool_id))
                else:
                    self.info("[%08X] <delete_host> deallocate public '%s' to address pool '%s' success"%(session.session_id, host.public_ip, pool_id))
                
        elif ComputeNetworkTypeEnum.share == host.network_type:
            
            if not bool(host.network):
                pool_id = host.network_source
                public_ip = host.public_ip
                port = [host.public_port]
                if 0 != len(host.port):
                    for allocated_port in host.port:
                        port.append(allocated_port.public_port)
                        
                if not self.port_manager.deallocate(pool_id, public_ip, port):
                    self.warn("[%08X] <delete_host> deallocate %d port in ip '%s' to port pool '%s' fail"%(session.session_id, len(port), public_ip, pool_id))
                else:
                    self.info("[%08X] <delete_host> deallocate %d port in ip '%s' to port pool '%s' success"%(session.session_id, len(port), public_ip, pool_id))
            
        #-----------
            
        self.config_manager.removeHost(session.target)
               
        #--------------
            
                
        forwarder_id = host.forwarder
        
        if forwarder_id:
            
            if not self.forwarder_manager.delete(forwarder_id):
                self.warn("[%08X] <delete_host> delete forwarder '%s' fail"%(session.session_id, forwarder_id))
            else:
                self.info("[%08X] <delete_host> delete forwarder '%s' success"%(session.session_id, forwarder_id))
                
            ##check ir
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            if default_ir is None:
                self.warn("[%08X] <delete_host> try remove forwarder, but no intelligent router actived for host"%(session.session_id))
                response = getResponse(RequestDefine.delete_host)
                response.success = True
                response.session = session.request_session
                self.sendMessage(response, session.request_module)
                session.finish()
                return
            
            ##send to ir
            remove_request = getRequest(RequestDefine.remove_forwarder)
            remove_request.session = session.session_id
            
            remove_request.setString(ParamKeyDefine.uuid, forwarder_id)
            session.target = forwarder_id
            
            self.sendMessage(remove_request, default_ir)
            self.setTimer(session, self.operate_timeout)
            self.info("[%08X] <delete_host> request remove forwarder '%s' to intelligent router '%s'..."%(session.session_id, forwarder_id, default_ir))
            return        
        
        else:
            
            msg.session = session.request_session
            self.sendMessage(msg, session.request_module)
            session.finish()
            
        ########################
        
    def onDeleteFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <delete_host> delete host fail, id '%s'"% (session.session_id, session.target))
        self.taskFail(session)
        
    def onDeleteTimeout(self, msg, session):
        self.error("[%08X] <delete_host> delete host timeout, id '%s'"% (session.session_id, session.target))
        self.taskFail(session)

    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <delete_host> remove forwarder in intelligent router success, forwarder id '%s'"% (session.session_id, session.target))
        response = getResponse(RequestDefine.delete_host)
        response.success = True
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()        

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <delete_host> remove forwarder in intelligent router fail, forwarder id '%s'"% (session.session_id, session.target))
        self.taskFail(session)
        
    def onRemoveTimeout(self, msg, session):
        self.error("[%08X] <delete_host> remove forwarder in intelligent router timeout, forwarder id '%s'"% (session.session_id, session.target))
        self.taskFail(session)




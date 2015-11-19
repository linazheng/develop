#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse,\
    EventDefine, getRequest
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage
from host_forwarder import ForwarderTypeEnum, HostForwarder
from compute_pool import ComputeNetworkTypeEnum
from network_info import NetworkStatus



class AttachHostTask(BaseTask):
    
    
    operate_timeout = 10
    
    
    def __init__(self, task_type, messsage_handler, network_manager, config_manager, forwarder_manager, address_manager, port_manager):
        self.network_manager    = network_manager
        self.config_manager     = config_manager
        self.forwarder_manager  = forwarder_manager
        self.address_manager    = address_manager
        self.port_manager       = port_manager
        logger_name = "task.attach_host"
        BaseTask.__init__(self, task_type, RequestDefine.attach_host, messsage_handler, logger_name)
        
        stAttachSuccess = 2
        stRemoveForwarderSuccess = 3
        self.addState(stAttachSuccess)
        self.addState(stRemoveForwarderSuccess)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.attach_host, result_success, self.onAttachSuccess, stAttachSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.attach_host, result_fail,    self.onAttachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,       result_any,     self.onAttachTimeout)        

        # stAttachSuccess
        self.addTransferRule(stAttachSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveSuccess, stRemoveForwarderSuccess)
        self.addTransferRule(stAttachSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail,    self.onRemoveFail)
        self.addTransferRule(stAttachSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder,    result_success, self.onAddSuccess)
        self.addTransferRule(stAttachSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder,    result_fail,    self.onAddFail)
        self.addTransferRule(stAttachSuccess, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onRemoveOrAddTimeout)
        
        # stRemoveForwarderSuccess
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddSuccess)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail,    self.onAddFail)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onAddTimeout)
        

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"]        = request.getString(ParamKeyDefine.uuid)
        _parameter["host"]        = request.getString(ParamKeyDefine.host)
        
        session._ext_data = {}
        session._ext_data["parameter"] = _parameter
        
        self.info("[%08X] <attach_host> receive attach host request from '%s', parameter: %s" % (session.session_id, 
                                                                                                 session.request_module, 
                                                                                                 _parameter))
        
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <attach_host> attach host fail, invalid network '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        session._ext_data["network_info"] = _networkInfo
        
        if _parameter["host"] in _networkInfo.hosts:
            self.error("[%08X] <attach_host> attach host fail, host '%s' attached already to network '%s'" % (session.session_id, _parameter["host"], _parameter["uuid"]))
            self.taskFail(session)
            return
        
        _host = self.config_manager.getHost(_parameter["host"])
        if _host==None:
            self.error("[%08X] <attach_host> attach host fail, invalid host '%s'" % (session.session_id, _parameter["host"]))
            self.taskFail(session)
            return
        
        
        if len(_host.network)>0:
            self.error("[%08X] <attach_host> attach host fail, host '%s' attached to network '%s' already." % (session.session_id, _parameter["host"], _host.network))
            self.taskFail(session)
            return
            
        session._ext_data["host"] = _host
        
        #------------------
        
        _host_dict = {}
        session._ext_data["host_dict"] = _host_dict
        
        #
        _vpc_ips = _networkInfo.allocateIp(1)
        if _vpc_ips==None:
            self.error("[%08X] <attach_host> attach host fail, not enough vpc ip" % (session.session_id))
            self.taskFail(session)
            return
        
        # _host.vpc_ip = _vpc_ips[0]
        _host_dict["vpc_ip"] = _vpc_ips[0]
        
        self.info("[%08X] <attach_host> vpc ip '%s' was allocated to host '%s'" % (session.session_id, _host_dict["vpc_ip"], _host.name))
        
        
        # create forwarder for host
        if not bool(_host.forwarder):
            if _host.network_type != ComputeNetworkTypeEnum.private:
                self.error("[%08X] attach host fail, host '%s'('%s') forwarder not found, network type '%d'" %
                           (session.session_id, _host.name, _host.uuid, _host.network_type))
                self.taskFail(session)
                return
            # HostForwarder
            forwarder = HostForwarder()
            
            forwarder.type           = ForwarderTypeEnum.vpc
            forwarder.host_id        = _host.uuid
            forwarder.host_name      = _host.name
            forwarder.server_ip      = _host.server_ip
            forwarder.server_monitor = _host.server_port
            forwarder.vpc_ip         = _host_dict["vpc_ip"] # _host.vpc_ip
            forwarder.vpc_range      = "%s/%s" % (_networkInfo.network_address, _networkInfo.netmask)
            
            self.forwarder_manager.create(forwarder)
            session._ext_data["new_forwarder"] = forwarder
            
#             if not self.forwarder_manager.create(forwarder):
#                 # release vpc ip
#                 _networkInfo.deallocateIp(_host.vpc_ip)
#                 
#                 self.error("[%08X] <attach_host> attach host fail, can't create forwarder" % (session.session_id))
#                 self.taskFail(session)
#                 return
            
            # _host.forwarder = forwarder.uuid
            _host_dict["forwarder"] = forwarder.uuid
            self.info("[%08X] <attach_host> create forwarder for host '%s'" % (session.session_id, _host.uuid))
            
        else:
            
            _host_dict["forwarder"] = _host.forwarder
        
        #------------------------
        
        self.info("[%08X] <attach_host> request attach host '%s'('%s') to compute node '%s'" % (session.session_id, _host.name, _host.uuid, _host.container))
        self.setTimer(session, self.operate_timeout)
        
        # send to node client to release resource of host
        msg = getRequest(RequestDefine.attach_host)
        msg.session = session.session_id
        
        msg.setString(ParamKeyDefine.uuid,            _parameter["host"]);
        msg.setString(ParamKeyDefine.forward,         _host_dict["forwarder"]);
        msg.setString(ParamKeyDefine.network,         _parameter["uuid"]);
        msg.setString(ParamKeyDefine.network_address, _networkInfo.network_address);
        msg.setUInt(ParamKeyDefine.netmask,           _networkInfo.netmask);
        msg.setString(ParamKeyDefine.ip,              _host_dict["vpc_ip"]);
        
        self.sendMessage(msg, _host.container)
        

    #--------------
    
    
    def onAttachSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _parameter   = session._ext_data["parameter"]
        _networkInfo = session._ext_data["network_info"] 
        _host        = session._ext_data["host"]
        _host_dict   = session._ext_data["host_dict"]
        
        self.info("[%08X] <attach_host> attach host on node client success, host '%s'" % (session.session_id, _parameter["host"]))
        
        # deallocate host resource
        
        if ComputeNetworkTypeEnum.monopoly == _host.network_type:
            
            pool_id = _host.network_source
            if self.address_manager.deallocate(pool_id, _host.public_ip):
                # _host.public_ip = ""
                _host_dict["public_ip"] = ""
                self.info("[%08X] <attach_host> deallocate public '%s' to address pool '%s' success"%(session.session_id, _host.public_ip, pool_id))
            else:
                self.warn("[%08X] <attach_host> deallocate public '%s' to address pool '%s' fail"%(session.session_id, _host.public_ip, pool_id))
        
        elif ComputeNetworkTypeEnum.share == _host.network_type:
            
            if not bool(_host.network):
                pool_id   = _host.network_source
                public_ip = _host.public_ip
                port      = [_host.public_port]
                
                if 0 != len(_host.port):
                    for allocated_port in _host.port:
                        port.append(allocated_port.public_port)
                        
                if self.port_manager.deallocate(pool_id, public_ip, port):
                    # _host.public_ip = ""
                    # _host.public_port = 0
                    # _host.port = []
                    _host_dict["public_ip"]   = ""
                    _host_dict["public_port"] = 0
                    _host_dict["port"]        = []
                    self.info("[%08X] <attach_host> deallocate %d port in ip '%s' to port pool '%s' success"%(session.session_id, len(port), public_ip, pool_id))
                else:
                    self.warn("[%08X] <attach_host> deallocate %d port in ip '%s' to port pool '%s' fail"%(session.session_id, len(port), public_ip, pool_id))
        else:
            _host.forwarder = _host_dict["forwarder"]
        
#         # attach host
#         self._attachHost(msg, session)
        if not self.network_manager.attachHost(_parameter["uuid"], _parameter["host"]):
            # release vpc ip
            # _networkInfo.deallocateIp(_host.vpc_ip)
            _networkInfo.deallocateIp(_host_dict["vpc_ip"])
            
            self.error("[%08X] <attach_host> attach host fail, network '%s', host '%s'" % (session.session_id, _parameter["uuid"], _parameter["host"]))
            self.taskFail(session)
            return
        
        # _host.network = _parameter["uuid"]
        _host_dict["network"] = _parameter["uuid"]
         
        self.info("[%08X] <attach_host> attach host success, network '%s', host '%s'" % (session.session_id, _parameter["uuid"], _parameter["host"]))
        self.network_manager.saveNetworkInfo(_parameter["uuid"])

        
        # HostForwarder
        forwarder = self.forwarder_manager.get(_host.forwarder, copy=True)
        if forwarder==None:
            # release vpc ip
            _networkInfo.deallocateIp(_host.vpc_ip)
            self.error("[%08X] <attach_host> attach host fail, forwarder not found" % (session.session_id))
            self.taskFail(session)
            return
        
        session._ext_data["forwarder"] = forwarder
        
        forwarder.type              = ForwarderTypeEnum.vpc
        # set vpc_ip
        forwarder.vpc_ip            = _host_dict["vpc_ip"]
        # set vpc_range
        forwarder.vpc_range         = "%s/%s" % (_networkInfo.network_address, _networkInfo.netmask)
        # clear public_ip
        forwarder.public_ip         = []
        # clear port
        forwarder.port              = []
        # clear output_port_range
        forwarder.output_port_range = []
        
        # remove forwarder in cs
        forwarder_id = _host_dict["forwarder"]
        
        # vpc network is disabled, no need to refresh forwarder
        if _networkInfo.status==NetworkStatus.disabled:
            forwarder.enable = True if (_networkInfo.status==NetworkStatus.enabled) else False
            
        #
        self.forwarder_manager.put(forwarder)
        self.config_manager.modifyHost(_host.uuid, _host_dict)
        
        # get default ir
        _default_ir = self.message_handler.getDefaultIntelligentRouter()
        if _default_ir == None:
            self.warn("[%08X] <attach_host> attach host fail, no intelligent router actived for host"%(session.session_id))
            
            # send respone
            response = getResponse(RequestDefine.attach_host)
            response.success = False
            response.session = session.request_session
            self.sendMessage(response, session.request_module)
            session.finish()
            return
        
        session._ext_data["default_ir"] = _default_ir
        
        if _host.network_type in (ComputeNetworkTypeEnum.monopoly, ComputeNetworkTypeEnum.share):
            # remove forwarder
            remove_request = getRequest(RequestDefine.remove_forwarder)
            remove_request.session = session.session_id
            remove_request.setString(ParamKeyDefine.uuid, forwarder_id)
            self.sendMessage(remove_request, _default_ir)
        else:
            # add forwarder
            add_request = getRequest(RequestDefine.add_forwarder)
            add_request.session = session.session_id
            
            add_request.setString(ParamKeyDefine.uuid,            forwarder.uuid)
            add_request.setUInt(ParamKeyDefine.type,              ForwarderTypeEnum.vpc)
            add_request.setString(ParamKeyDefine.host,            forwarder.host_id)
            add_request.setString(ParamKeyDefine.name,            forwarder.host_name)
            add_request.setUIntArray(ParamKeyDefine.range,        forwarder.output_port_range)
            add_request.setStringArray(ParamKeyDefine.ip,         [forwarder.server_ip])
            add_request.setString(ParamKeyDefine.network_address, forwarder.vpc_ip)              # add_request.setString(ParamKeyDefine.vpc_ip,          forwarder.vpc_ip)
            add_request.setString(ParamKeyDefine.address,         _networkInfo.network_address)                      # add_request.setString(ParamKeyDefine.vpc_range,       forwarder.vpc_range)
            add_request.setUInt(ParamKeyDefine.netmask,           _networkInfo.netmask)
            add_request.setUIntArray(ParamKeyDefine.display_port, [forwarder.server_monitor, forwarder.public_monitor])
            add_request.setUIntArray(ParamKeyDefine.port,         [])
            add_request.setUInt(ParamKeyDefine.status,            _networkInfo.status)
            
            self.sendMessage(add_request, _default_ir)
        
        self.setTimer(session, self.operate_timeout)
        
        
    def onAttachFail(self, msg, session):
        self.clearTimer(session)
        
        _parameter     = session._ext_data["parameter"]
        _networkInfo   = session._ext_data["network_info"]
        _host_dict     = session._ext_data["host_dict"]
        _new_forwarder = session._ext_data.get("new_forwarder", None)
        
        if _host_dict.has_key("vpc_ip"):
            _networkInfo.deallocateIp(_host_dict["vpc_ip"])
            
        if _new_forwarder!=None:
            self.forwarder_manager.delete(_new_forwarder.uuid)
        
        self.error("[%08X] <attach_host> attach host on node client fail, network '%s', host '%s'"% (session.session_id, _parameter["uuid"], _parameter["host"]))
        self.taskFail(session)
        
        
    def onAttachTimeout(self, msg, session):
        self.clearTimer(session)
        
        _parameter     = session._ext_data["parameter"]
        _networkInfo   = session._ext_data["network_info"]
        _host_dict     = session._ext_data["host_dict"]
        _new_forwarder = session._ext_data.get("new_forwarder", None)
        
        if _host_dict.has_key("vpc_ip"):
            _networkInfo.deallocateIp(_host_dict["vpc_ip"])
            
        if _new_forwarder!=None:
            self.forwarder_manager.delete(_new_forwarder.uuid)
        
        self.error("[%08X] <attach_host> attach host on node client timeout, network '%s', host '%s'"% (session.session_id, _parameter["uuid"], _parameter["host"]))
        self.taskFail(session)
        
        
    #--------------
        
        
    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)
        
        _default_ir  = session._ext_data["default_ir"] 
        forwarder    = session._ext_data["forwarder"] 
        _networkInfo = session._ext_data["network_info"]
        
        self.info("[%08X] <attach_host> remove forwarder in intelligent router success, forwarder id '%s'"% (session.session_id, forwarder.uuid))
        
        _address = ""
        _netmask = ""
        if forwarder.vpc_range:
            _address, _netmask = forwarder.vpc_range.split("/")
        
        # add forwarder
        add_request = getRequest(RequestDefine.add_forwarder)
        add_request.session = session.session_id
        
        add_request.setString(ParamKeyDefine.uuid,            forwarder.uuid)
        add_request.setUInt(ParamKeyDefine.type,              ForwarderTypeEnum.vpc)
        add_request.setString(ParamKeyDefine.host,            forwarder.host_id)
        add_request.setString(ParamKeyDefine.name,            forwarder.host_name)
        add_request.setUIntArray(ParamKeyDefine.range,        forwarder.output_port_range)
        add_request.setStringArray(ParamKeyDefine.ip,         [forwarder.server_ip])
        add_request.setString(ParamKeyDefine.network_address, forwarder.vpc_ip)              # add_request.setString(ParamKeyDefine.vpc_ip,          forwarder.vpc_ip)
        add_request.setString(ParamKeyDefine.address,         _address)                      # add_request.setString(ParamKeyDefine.vpc_range,       forwarder.vpc_range)
        add_request.setUInt(ParamKeyDefine.netmask,           int(_netmask))
        add_request.setUIntArray(ParamKeyDefine.display_port, [forwarder.server_monitor, forwarder.public_monitor])
        add_request.setUIntArray(ParamKeyDefine.port,         [])
        add_request.setUInt(ParamKeyDefine.status,            _networkInfo.status)
        
        self.sendMessage(add_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        forwarder = session._ext_data["forwarder"] 
        self.error("[%08X] <attach_host> remove forwarder in intelligent router fail, forwarder id '%s'"% (session.session_id, forwarder.uuid))
        self.taskFail(session)
        
        
    def onRemoveOrAddTimeout(self, msg, session):
        forwarder = session._ext_data["forwarder"]
        default_ir  = session._ext_data["default_ir"]
        host_info = session._ext_data["host"]
        if host_info.network_type in (ComputeNetworkTypeEnum.monopoly, ComputeNetworkTypeEnum.share):
            self.error("[%08X] attach host timeout, remove forwarder in intelligent router '%s' timeout, forwarder id '%s'"%
                       (session.session_id, default_ir, forwarder.uuid))
        else:
            self.error("[%08X] attach host timeout, add forwarder in intelligent router '%s' timeout, forwarder id '%s'"%
                       (session.session_id, default_ir, forwarder.uuid))
        self.taskFail(session)

        
    #--------------
    
    
    def onAddSuccess(self, msg, session):
        self.clearTimer(session)
        
        forwarder = session._ext_data["forwarder"]
        host      = session._ext_data["host"]
        network_info = session._ext_data["network_info"]
        
        self.info("[%08X] <attach_host> add forwarder in intelligent router success, forwarder id '%s'"% (session.session_id, forwarder.uuid))
        
        response = getResponse(RequestDefine.attach_host)
        response.success = True
        response.session = session.request_session
        
        response.setString(ParamKeyDefine.network_address, host.vpc_ip)
        
        self.sendMessage(response, session.request_module)
        self.info("[%08X] attach host success, network id '%s'('%s'), host '%s'('%s')" %
                  (session.session_id, network_info.name, network_info.uuid, host.name, host.uuid))
        session.finish()        


    def onAddFail(self, msg, session):
        self.clearTimer(session)
        forwarder = session._ext_data["forwarder"]
        self.error("[%08X] <attach_host> add forwarder in intelligent router fail, forwarder id '%s'"% (session.session_id, forwarder.uuid))
        self.taskFail(session)
        
        
    def onAddTimeout(self, msg, session):
        forwarder = session._ext_data["forwarder"]
        self.error("[%08X] <attach_host> add forwarder in intelligent router timeout, forwarder id '%s'"% (session.session_id, forwarder.uuid))
        self.taskFail(session)
        
    
    #------------
        
        
#     def _attachHost(self, msg, session):
#         
#         _parameter   = session._ext_data["parameter"]
#         _host        = session._ext_data["host"]
#         _networkInfo = session._ext_data["network_info"]
#         
#         if not self.network_manager.attachHost(_parameter["uuid"], _parameter["host"]):
#             # release vpc ip
#             _networkInfo.deallocateIp(_host.vpc_ip)
#             
#             self.error("[%08X] <attach_host> attach host fail, network '%s', host '%s'" % (session.session_id, _parameter["uuid"], _parameter["host"]))
#             self.taskFail(session)
#             return
#         
#         _host.network = _parameter["uuid"]
#          
#         self.info("[%08X] <attach_host> attach host success, network '%s', host '%s'" % (session.session_id, _parameter["uuid"], _parameter["host"]))
#         self.network_manager.saveNetworkInfo(_parameter["uuid"])

        
        
        
        


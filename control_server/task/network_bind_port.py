#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse,\
    getRequest, EventDefine
from host_info import HostPort
from host_forwarder import ForwarderPort, ForwarderTypeEnum
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage
from common import dict_util



class NetworkBindPortTask(BaseTask):
    
    
    operate_timeout = 30
    
    
    def __init__(self, task_type, messsage_handler, network_manager, config_manager, forwarder_manager):
        self.network_manager    = network_manager
        self.config_manager     = config_manager
        self.forwarder_manager  = forwarder_manager
        logger_name = "task.network_bind_port"
        BaseTask.__init__(self, task_type, RequestDefine.network_bind_port, messsage_handler, logger_name)
        
        
        stNodeClientBindPortSuccess = 2
        stRemoveForwarderSuccess = 3
        stAddForwarderSuccess = 4
        self.addState(stNodeClientBindPortSuccess)
        self.addState(stRemoveForwarderSuccess)
        self.addState(stAddForwarderSuccess)
        
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_success, self.onBindSuccess, stNodeClientBindPortSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_fail,    self.onBindFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onBindTimeout)
        
        # stNodeClientBindPortSuccess
        self.addTransferRule(stNodeClientBindPortSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveSuccess, stRemoveForwarderSuccess)
        self.addTransferRule(stNodeClientBindPortSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail,    self.onRemoveFail)
        self.addTransferRule(stNodeClientBindPortSuccess, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onRemoveTimeout)
        
        # stRemoveForwarderSuccess
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddSuccess, stAddForwarderSuccess)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail,    self.onAddFail)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onAddTimeout)
        
        # stAddForwarderSuccess
        self.addTransferRule(stAddForwarderSuccess, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_success, self.onBindSuccess, stNodeClientBindPortSuccess)
        self.addTransferRule(stAddForwarderSuccess, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_fail,    self.onBindFail)
        self.addTransferRule(stAddForwarderSuccess, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onBindTimeout)
        


    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        session._ext_data = {}
        
        _parameter = {}
        _parameter["uuid"] = request.getString(ParamKeyDefine.uuid)
        _parameter["port"] = request.getStringArrayArray(ParamKeyDefine.port)
        
        self.info("[%08X] <network_bind_port> receive network bind port request from '%s', parameter: %s" % (session.session_id, 
                                                                                                             session.request_module, 
                                                                                                             _parameter))
        
        # get default ir
        _default_ir = self.message_handler.getDefaultIntelligentRouter()
        if _default_ir == None:
            self.warn("[%08X] <network_bind_port> network bind port fail, no intelligent router actived for host"%(session.session_id))
            
            # send respone
            response = getResponse(RequestDefine.network_bind_port)
            response.session = session.request_session
            response.success = False
             
            response.setStringArrayArray(ParamKeyDefine.port, [])    
             
            self.sendMessage(response, session.request_module)
            session.finish()
            return
        
        session._ext_data["default_ir"] = _default_ir
        
        # found network
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <network_bind_port> network not found, invalid uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        _success_ports = []
        _fail_ports = []
        
        # key: host uuid, value: HostInfo
        _hosts = {}
        # key: forwarder uuid, value: HostForwarder
        _forwarders = {}
        
        # handle port
        for _port_info_arr in _parameter["port"]:
            
            try:
                
                if len(_port_info_arr)!=5:
                    self.error("[%08X] <network_bind_port> network bind port fail, wrong port parameter: %s" % (session.session_id, _port_info_arr))
                    _fail_ports.append(_port_info_arr)
                    continue;
                
                _protocol    = int(_port_info_arr[0])
                _public_ip   = str(_port_info_arr[1])
                _public_port = int(_port_info_arr[2])
                _host_uuid   = str(_port_info_arr[3])
                _host_port   = int(_port_info_arr[4])
                
            except:
                self.exception("[%08X] <network_bind_port> network bind port fail, wrong port parameter: %s" % (session.session_id, _port_info_arr))
                _fail_ports.append(_port_info_arr)
                continue
            
            if _public_ip not in _networkInfo.public_ips:
                self.error("[%08X] <network_bind_port> network bind port fail, public ip '%s' is not allocated to network" % (session.session_id, _public_ip))
                _fail_ports.append(_port_info_arr)
                continue
            
            _bound_port_key   = "%s:%s:%s" % (_protocol, _public_ip, _public_port)
            _bound_port_value = "%s:%s" % (_host_uuid, _host_port)
            if _networkInfo.bound_ports.has_key(_bound_port_key):
                self.error("[%08X] <network_bind_port> network bind port fail, public port '%s' bound already" % (session.session_id, _bound_port_key))
                _fail_ports.append(_port_info_arr)
                continue
            
            # check for all protocol
            _bound_port_key_for_all   = "%s:%s:%s" % (0, _public_ip, _public_port)
            if _networkInfo.bound_ports.has_key(_bound_port_key_for_all):
                self.error("[%08X] <network_bind_port> network bind port fail, public port '%s' bound already for all protocol,  all protocol key '%s'" % (session.session_id, _bound_port_key, _bound_port_key_for_all))
                _fail_ports.append(_port_info_arr)
                continue
                
            if _host_uuid not in _networkInfo.hosts:
                self.error("[%08X] <network_bind_port> network bind port fail, host '%s' does not attach to network" % (session.session_id, _host_uuid))
                _fail_ports.append(_port_info_arr)
                continue
            
            _host = self.config_manager.getHost(_host_uuid)
            if _host==None:
                self.error("[%08X] <network_bind_port> network bind port fail, host '%s' not found" % (session.session_id, _host_uuid))
                _fail_ports.append(_port_info_arr)
                continue
            
            # if a host is in vpc network, it definitely has a forwarder
            _forwarder = _forwarders.get(_host.forwarder, None)
            
            if _forwarder==None:
                _forwarder = self.forwarder_manager.get(_host.forwarder, copy=True)
                
            if _forwarder==None:
                self.error("[%08X] <network_bind_port> network bind port fail, forwarder '%s' not found" % (session.session_id, _host.forwarder))
                _fail_ports.append(_port_info_arr)
                continue
            
            _networkInfo.bound_ports[_bound_port_key] = _bound_port_value
            
            _hostPort = HostPort()
            _hostPort.protocol     = _protocol
            _hostPort.public_ip    = _public_ip
            _hostPort.public_port  = _public_port
            _hostPort.host_port    = _host_port
            _host.port.append(_hostPort)
            
            _forwarderPort = ForwarderPort()
            _forwarderPort.protocol    = _protocol
            _forwarderPort.public_ip   = _public_ip
            _forwarderPort.public_port = _public_port
            _forwarderPort.host_port   = _host_port
            _forwarder.port.append(_forwarderPort)
            
            _hosts[_host.uuid] = _host
            _forwarders[_forwarder.uuid] = _forwarder
            
            _success_ports.append(_port_info_arr)
            
        # putting into forwarder_manager aim at calculating of crc 
        for _forwarder in _forwarders.values():
            self.forwarder_manager.put(_forwarder)
            
        self.network_manager.saveNetworkInfo(_parameter["uuid"])
        
        session._ext_data["hosts"]         = _hosts
        session._ext_data["forwarders"]    = _forwarders
        session._ext_data["success_ports"] = _success_ports
        
        self._refreshForwarder(session)
        
        
    def _refreshForwarder(self, session):
        _hosts      = session._ext_data["hosts"]
        
        try:
            _host = _hosts.popitem()[1]
            session._ext_data["host_in_refreshing"] = _host
            
            _bind_port = []
            for _host_port in _host.port:
                _bind_port.append(str(_host_port.protocol))
                _bind_port.append(str(_host_port.public_ip))
                _bind_port.append(str(_host_port.public_port))
                _bind_port.append(str(_host_port.host_port))
            
            # send network_bind_port to node client
            bind_request = getRequest(RequestDefine.network_bind_port)
            bind_request.session = session.session_id
            
            bind_request.setString(ParamKeyDefine.uuid,       _host.uuid)
            bind_request.setStringArray(ParamKeyDefine.port,  _bind_port)
            
            self.info("[%08X] <network_bind_port> send network_bind_port request to node client '%s'" % (session.session_id, _host.container))
            
            self.sendMessage(bind_request, _host.container)
            self.setTimer(session, self.operate_timeout)
            
        except KeyError:
            self.info("[%08X] <network_bind_port> no other host unhandled." % (session.session_id))
            self._sendResponse(session)
          
          
    #-------------------------
    
    
    def onBindSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir = session._ext_data["default_ir"]
        _forwarders = session._ext_data["forwarders"]
        _host       = session._ext_data["host_in_refreshing"]
        
        self.info("[%08X] <network_bind_port> bind host port(s) in node client success, host '%s'" % (session.session_id, _host.uuid))
        
        _forwarder = _forwarders[_host.forwarder]
        
        # remove forwarder
        remove_request = getRequest(RequestDefine.remove_forwarder)
        remove_request.session = session.session_id
        
        remove_request.setString(ParamKeyDefine.uuid, _host.forwarder)
        
        self.info("[%08X] <network_bind_port> send remove forwarder request to intelligent router '%s'" % (session.session_id, _default_ir))
        
        self.sendMessage(remove_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        
        
    def onBindFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.error("[%08X] <network_bind_port> bind host port(s) in node client fail, host '%s'" % (session.session_id, _host.uuid))
        self.taskFail(session)
        
        
    def onBindTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.error("[%08X] <network_bind_port> bind host port(s) in node client timeout, host '%s'" % (session.session_id, _host.uuid))
        self.taskFail(session)
    
    
    #-------------------------  
    
    
    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir = session._ext_data["default_ir"]
        _forwarders = session._ext_data["forwarders"]
        _host       = session._ext_data["host_in_refreshing"]
        
        self.info("[%08X] <network_bind_port> remove forwarder '%s' success" % (session.session_id, _host.forwarder))
        
        _forwarder = _forwarders[_host.forwarder]
        
        _public_ip_arr = []
        _forward_vpc_port = []
        for _host_port in _host.port:
            try:
                _public_ip_index = _public_ip_arr.index(_host_port.public_ip)
            except:
                _public_ip_arr.append(_host_port.public_ip)
                _public_ip_index = len(_public_ip_arr) - 1
            
            # HostPort
            _forward_vpc_port.append(_host_port.protocol)
            _forward_vpc_port.append(_public_ip_index)
            _forward_vpc_port.append(_host_port.public_port)
            _forward_vpc_port.append(_host_port.host_port)
            
        
        _address = ""
        _netmask = ""
        if _forwarder.vpc_range:
            _address, _netmask = _forwarder.vpc_range.split("/")

        _arg_ip = [_forwarder.server_ip]
        _arg_ip.extend(_public_ip_arr)
        
        # add forwarder
        add_request = getRequest(RequestDefine.add_forwarder)
        add_request.session = session.session_id
        
        add_request.setString(ParamKeyDefine.uuid,            _forwarder.uuid)
        add_request.setUInt(ParamKeyDefine.type,              ForwarderTypeEnum.vpc)
        add_request.setString(ParamKeyDefine.host,            _forwarder.host_id)
        add_request.setString(ParamKeyDefine.name,            _forwarder.host_name)
        add_request.setUIntArray(ParamKeyDefine.range,        _forwarder.output_port_range)
        add_request.setStringArray(ParamKeyDefine.ip,         _arg_ip)
        add_request.setString(ParamKeyDefine.network_address, _forwarder.vpc_ip)     # add_request.setString(ParamKeyDefine.vpc_ip,          _forwarder.vpc_ip)
        add_request.setString(ParamKeyDefine.address,         _address)              # add_request.setString(ParamKeyDefine.vpc_range,       _forwarder.vpc_range)
        add_request.setUInt(ParamKeyDefine.netmask,           int(_netmask))
        add_request.setUIntArray(ParamKeyDefine.display_port, [_forwarder.server_monitor, _forwarder.public_monitor])
        add_request.setUIntArray(ParamKeyDefine.port,         [])
        add_request.setUIntArray(ParamKeyDefine.forward,      _forward_vpc_port)
        add_request.setUInt(ParamKeyDefine.status,            1 if (_forwarder.enable==True) else 0)
        
        self.info("[%08X] <network_bind_port> send add forwarder request to intelligent router '%s'" % (session.session_id, _default_ir))
        
        self.sendMessage(add_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        
        
    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.info("[%08X] <network_bind_port> network bind port fail, remove forwarder fail" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    def onRemoveTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.info("[%08X] <network_bind_port> network bind port timeout, remove forwarder timeout" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
        
    #-------------------------  
    
    
    def onAddSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir = session._ext_data["default_ir"]
        _hosts      = session._ext_data["hosts"]
        _forwarders = session._ext_data["forwarders"]
        _host       = session._ext_data["host_in_refreshing"]
        
        self.info("[%08X] <network_bind_port> add forwarder '%s' success" % (session.session_id, _host.forwarder))
        self._refreshForwarder(session)
        
        
        
    def onAddFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.info("[%08X] <network_bind_port> network bind port fail, add forwarder '%s' fail" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    def onAddTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.info("[%08X] <network_bind_port> network bind port timeout, add forwarder '%s' timeout" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    #----------------------
    
    
    def _sendResponse(self, session):
        
        _success_ports = session._ext_data["success_ports"]
        
        response = getResponse(RequestDefine.network_bind_port)
        response.session = session.request_session
        response.success = True
         
        response.setStringArrayArray(ParamKeyDefine.port, _success_ports)    
         
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
        
        
        
        
        
        
        
        
        


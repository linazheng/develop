#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse,\
    getRequest, EventDefine
from host_forwarder import ForwarderTypeEnum
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage



class NetworkUnbindPortTask(BaseTask):
    
    
    operate_timeout = 30
    
    
    def __init__(self, task_type, messsage_handler, network_manager, config_manager, forwarder_manager):
        self.network_manager    = network_manager
        self.config_manager     = config_manager
        self.forwarder_manager  = forwarder_manager
        logger_name = "task.network_unbind_port"
        BaseTask.__init__(self, task_type, RequestDefine.network_unbind_port, messsage_handler, logger_name)
        
        stNodeClientUnbindPortSuccess = 2
        stRemoveForwarderSuccess = 3
        stAddForwarderSuccess = 4
        self.addState(stNodeClientUnbindPortSuccess)
        self.addState(stRemoveForwarderSuccess)
        self.addState(stAddForwarderSuccess)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_success, self.onUnbindSuccess, stNodeClientUnbindPortSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_fail,    self.onUnbindFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,               result_any,     self.onUnbindTimeout)
        
        # stNodeClientUnbindPortSuccess
        self.addTransferRule(stNodeClientUnbindPortSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveSuccess, stRemoveForwarderSuccess)
        self.addTransferRule(stNodeClientUnbindPortSuccess, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail,    self.onRemoveFail)
        self.addTransferRule(stNodeClientUnbindPortSuccess, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onRemoveTimeout)
        
        # stRemoveForwarderSuccess
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddSuccess, stAddForwarderSuccess)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail,    self.onAddFail)
        self.addTransferRule(stRemoveForwarderSuccess, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onAddTimeout)
        
        # stAddForwarderSuccess
        self.addTransferRule(stAddForwarderSuccess, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_success, self.onUnbindSuccess, stNodeClientUnbindPortSuccess)
        self.addTransferRule(stAddForwarderSuccess, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_fail,    self.onUnbindFail)
        self.addTransferRule(stAddForwarderSuccess, AppMessage.EVENT,    EventDefine.timeout,               result_any,     self.onUnbindTimeout)
        
    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        session._ext_data = {}
        
        _parameter = {}
        _parameter["uuid"]        = request.getString(ParamKeyDefine.uuid)
        _parameter["port"]        = request.getStringArrayArray(ParamKeyDefine.port)
        
        self.info("[%08X] <network_unbind_port> receive network unbind port request from '%s', parameter: %s" % (session.session_id, 
                                                                                                                 session.request_module, 
                                                                                                                 _parameter))
        
        # get default ir
        _default_ir = self.message_handler.getDefaultIntelligentRouter()
        if _default_ir == None:
            self.warn("[%08X] <network_unbind_port> network unbind port fail, no intelligent router actived for host"%(session.session_id))
             
            # send respone
            response = getResponse(RequestDefine.network_unbind_port)
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
            self.error("[%08X] <network_unbind_port> network not found, invalid network uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        # key: host_uuid, value: set of (_protocol, _public_ip, _public_port, _host_port)
        _delete_ports = {}
        
        _success_ports = []
        _fail_ports = []
        
        # key: host uuid, value: HostInfo
        _hosts = {}
        # key: forwarder uuid, value: HostForwarder
        _forwarders = {}
        
        #
        _arg_port = _parameter["port"]
        for i in xrange(len(_arg_port)):
            
            _port_info = _arg_port[i]
            
            _protocol    = int(_port_info[0])
            _public_ip   = str(_port_info[1])
            _public_port = int(_port_info[2])
            
            _bound_port_key   = "%s:%s:%s" % (_protocol, _public_ip, _public_port)
            _bound_port_value = _networkInfo.bound_ports.pop(_bound_port_key, None)
            
            if _bound_port_value==None:
                self.error("[%08X] <network_unbind_port> network unbind port fail for '%s'" % (session.session_id, _bound_port_key))
                _fail_ports.append(_port_info)
                continue
                
            self.info("[%08X] <network_unbind_port> network unbind port success for '%s' -> '%s'" % (session.session_id, _bound_port_key, _bound_port_value))
            _success_ports.append(_port_info)
            
            _bound_port_info = _bound_port_value.split(":")
            _host_uuid = str(_bound_port_info[0])
            _host_port = int(_bound_port_info[1])
            
            # get host
            _host = self.config_manager.getHost(_host_uuid)
            if _host==None:
                self.error("[%08X] <network_unbind_port> network unbind port fail, host '%s' not found" % (session.session_id, _host_uuid))
                continue
            
            self._deleteHostPort(_host, _protocol, _public_ip, _public_port, _host_port)
            
            # get forwarder
            _forwarder = _forwarders.get(_host.forwarder, None)
            
            if _forwarder==None:
                _forwarder = self.forwarder_manager.get(_host.forwarder, copy=True)
                
            if _forwarder==None:
                self.error("[%08X] <network_unbind_port> network unbind port fail, forwarder '%s' not found" % (session.session_id, _host.forwarder))
                continue
            
            #
            if not _delete_ports.has_key(_host_uuid):
                _delete_port_set = set()
                _delete_ports[_host_uuid] = _delete_port_set
            else:
                _delete_port_set = _delete_ports[_host_uuid]
            _delete_port_set.add( (_protocol, _public_ip, _public_port, _host_port) )
            
            #
            self._deleteForwarderPort(_forwarder, _protocol, _public_ip, _public_port, _host_port)
            
            #
            _hosts[_host.uuid] = _host
            _forwarders[_forwarder.uuid] = _forwarder
            
            
        # putting into forwarder_manager aim at calculating of crc 
        for _forwarder in _forwarders.values():
            self.forwarder_manager.put(_forwarder)
            
            
        self.network_manager.saveNetworkInfo(_parameter["uuid"])
        
        session._ext_data["hosts"]         = _hosts
        session._ext_data["forwarders"]    = _forwarders
        session._ext_data["delete_ports"]  = _delete_ports
        session._ext_data["success_ports"] = _success_ports
        
        self._refreshForwarder(session)
        
        
    def _refreshForwarder(self, session):
        _hosts        = session._ext_data["hosts"] 
        _delete_ports = session._ext_data["delete_ports"] 
        
        try:
            _deleting_port_info = _delete_ports.popitem()
            session._ext_data["deleting_port_info"] = _deleting_port_info
            
            _host_uuid, _delete_port_set = _deleting_port_info
            _host = _hosts[_host_uuid]
            session._ext_data["host_in_refreshing"] = _host
            
            _delete_ports = []
            for _delete_port in _delete_port_set:
                _protocol, _public_ip, _public_port, _host_port = _delete_port
                _delete_ports.append(str(_protocol))
                _delete_ports.append(str(_public_ip))
                _delete_ports.append(str(_public_port))
                _delete_ports.append(str(_host_port))
            
            # send network_unbind_port to node client
            bind_request = getRequest(RequestDefine.network_unbind_port)
            bind_request.session = session.session_id
            
            bind_request.setString(ParamKeyDefine.uuid,       _host_uuid)
            bind_request.setStringArray(ParamKeyDefine.port,  _delete_ports)
            
            self.info("[%08X] <network_unbind_port> send network_unbind_port request to node client '%s'" % (session.session_id, _host.container))
            
            self.sendMessage(bind_request, _host.container)
            self.setTimer(session, self.operate_timeout)
            
        except KeyError:
            self.info("[%08X] <network_unbind_port> no other host unhandled." % (session.session_id))
            self._sendResponse(session)
          
          
    #----------------------
    
    
    def onUnbindSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir         = session._ext_data["default_ir"]
        _forwarders         = session._ext_data["forwarders"]
        _host               = session._ext_data["host_in_refreshing"] 
        
        self.info("[%08X] <network_unbind_port> unbind host port(s) in node client success, host '%s'" % (session.session_id, _host.uuid))
        
        _forwarder = _forwarders[_host.forwarder]
        
        # remove forwarder
        remove_request = getRequest(RequestDefine.remove_forwarder)
        remove_request.session = session.session_id
        
        remove_request.setString(ParamKeyDefine.uuid, _host.forwarder)
        
        self.info("[%08X] <network_unbind_port> send remove forwarder request to intelligent router '%s'" % (session.session_id, _default_ir))
        
        self.sendMessage(remove_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        
        
    def onUnbindFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.error("[%08X] <network_unbind_port> bind host port(s) in node client fail, host '%s'" % (session.session_id, _host.uuid))
        self.taskFail(session)
        
        
    def onUnbindTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.error("[%08X] <network_unbind_port> bind host port(s) in node client timeout, host '%s'" % (session.session_id, _host.uuid))
        self.taskFail(session)
    
    
    #---------------------
    
    
    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir         = session._ext_data["default_ir"]
        _forwarders         = session._ext_data["forwarders"]
        _host               = session._ext_data["host_in_refreshing"] 
        
        self.info("[%08X] <network_unbind_port> remove forwarder '%s' success" % (session.session_id, _host.forwarder))
        
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
        add_request.setString(ParamKeyDefine.network_address, _forwarder.vpc_ip)        # add_request.setString(ParamKeyDefine.vpc_ip,          _forwarder.vpc_ip)
        add_request.setString(ParamKeyDefine.address,         _address)                 # add_request.setString(ParamKeyDefine.vpc_range,       _forwarder.vpc_range)
        add_request.setUInt(ParamKeyDefine.netmask,           int(_netmask))
        add_request.setUIntArray(ParamKeyDefine.display_port, [_forwarder.server_monitor, _forwarder.public_monitor])
        add_request.setUIntArray(ParamKeyDefine.port,         [])
        add_request.setUIntArray(ParamKeyDefine.forward,    _forward_vpc_port)
        add_request.setUInt(ParamKeyDefine.status,     1 if (_forwarder.enable==True) else 0)
        
        self.info("[%08X] <network_unbind_port> send add forwarder request to intelligent router '%s'" % (session.session_id, _default_ir))
        
        self.sendMessage(add_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        
        
    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.info("[%08X] <network_unbind_port> network bind port fail, remove forwarder '%s' fail" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    def onRemoveTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.info("[%08X] <network_unbind_port> network bind port timeout, remove forwarder '%s' timeout" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    #----------------------
    
    
    def onAddSuccess(self, msg, session):
        self.clearTimer(session)   
        
        _default_ir = session._ext_data["default_ir"]
        _hosts      = session._ext_data["hosts"]
        _forwarders = session._ext_data["forwarders"]
        _host       = session._ext_data["host_in_refreshing"]
        
        self.info("[%08X] <network_unbind_port> add forwarder '%s' success" % (session.session_id, _host.forwarder))
        
        self._refreshForwarder(session)
        
        
    def onAddFail(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"]
        self.info("[%08X] <network_unbind_port> network bind port fail, add forwarder '%s' fail" % (session.session_id, _host.forwarder))
        self.taskFail(session)
        
        
    def onAddTimeout(self, msg, session):
        self.clearTimer(session)
        _host = session._ext_data["host_in_refreshing"] 
        self.info("[%08X] <network_unbind_port> network bind port timeout, add forwarder '%s' timeout" % (session.session_id, _host.forwarder))
        self.taskFail(session)
    
        
    #---------------------
        
    def _deleteHostPort(self, host, protocol, public_ip, public_port, host_port):
        if not bool(host.port):
            return 0
        
        _delete_count = 0
        _host_port_arr = host.port[:]
        for _host_port in _host_port_arr:
            if _host_port.protocol==int(protocol) and _host_port.public_ip==str(public_ip) and _host_port.public_port==int(public_port) and _host_port.host_port==int(host_port) :
                host.port.remove(_host_port)
                _delete_count += 1
                
        return _delete_count
        
    
    def _deleteForwarderPort(self, forwarder, protocol, public_ip, public_port, host_port):
        if not bool(forwarder.port):
            return 0
        
        _delete_count = 0
        _forwarder_port_arr = forwarder.port[:]
        for _forwarder_port in _forwarder_port_arr:
            if _forwarder_port.protocol==int(protocol) and _forwarder_port.public_ip==str(public_ip) and _forwarder_port.public_port==int(public_port) and _forwarder_port.host_port==int(host_port) :
                forwarder.port.remove(_forwarder_port)
                _delete_count += 1
                
        return _delete_count
        
    
    #----------------
    
    
    def _sendResponse(self, session):
        
        _success_ports = session._ext_data["success_ports"]
        
        response = getResponse(RequestDefine.network_unbind_port)
        response.session = session.request_session
        response.success = True
         
        response.setStringArrayArray(ParamKeyDefine.port, _success_ports)    
         
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
        
        
        
        
        
        
        
        


#!/usr/bin/python
from host_forwarder import HostForwarder, ForwarderPort
from common import dict_util
from compute_pool import ComputeNetworkTypeEnum
from host_info import HostPort, EnableLocalBackupEnum, EnableUsbExtEnum
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, EventDefine, ParamKeyDefine,\
    getRequest, getResponse
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage
from host_info import VideoTypeEnum

class ModifyHostTask(BaseTask):
    
    operate_timeout = 5
    
    def __init__(self, task_type, messsage_handler, config_manager, compute_pool_manager, port_manager, forwarder_manager):
        
        self.config_manager       = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.port_manager         = port_manager
        self.forwarder_manager    = forwarder_manager
        logger_name = "task.modify_host"
        BaseTask.__init__(self, task_type, RequestDefine.modify_host, messsage_handler, logger_name)
        
        stRemoveForwarder = 2
        stAddForwarder = 3
        self.addState(stRemoveForwarder)
        self.addState(stAddForwarder)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_host, result_success, self.onModifySuccess, stRemoveForwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_host, result_fail,    self.onModifyFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,       result_any,     self.onModifyTimeout)

        # stRemoveForwarder
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveSuccess, stAddForwarder)
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail,    self.onRemoveFail)
        self.addTransferRule(stRemoveForwarder, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onRemoveTimeout)        

        # stAddForwarder
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddSuccess)
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail,    self.onAddFail)
        self.addTransferRule(stAddForwarder, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onAddTimeout)        


    def invokeSession(self, session):
        """
        task start, must override
        """
        session._ext_data = {}
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"]               = request.getString(ParamKeyDefine.uuid)
        _parameter["host_name"]          = request.getString(ParamKeyDefine.name)
        _parameter["cpu_count"]          = request.getUInt(ParamKeyDefine.cpu_count)
        _parameter["memory"]             = request.getUInt(ParamKeyDefine.memory)
        _parameter["option"]             = request.getUIntArray(ParamKeyDefine.option)
        _parameter["port"]               = request.getUIntArray(ParamKeyDefine.port)
        _parameter["display"]            = request.getString(ParamKeyDefine.display)
        _parameter["authentication"]     = request.getString(ParamKeyDefine.authentication)
        _parameter["inbound_bandwidth"]  = request.getUInt(ParamKeyDefine.inbound_bandwidth)
        _parameter["outbound_bandwidth"] = request.getUInt(ParamKeyDefine.outbound_bandwidth)
        
        session._ext_data["parameter"] = _parameter
        
        uuid = _parameter["uuid"]
        port = _parameter["port"]
        
        self.info("[%08X] <modify_host> receive modify host request, uuid '%s', parameter: %s" % (session.session_id, 
                                                                                                  uuid, 
                                                                                                  dict_util.toDictionary(_parameter)))
        
        # instance of HostInfo
        host = self.config_manager.getHost(uuid)
        if host is None:
            self.error("[%08X] <modify_host> modify host fail, invalid id '%s'" % (session.session_id, uuid))
            self.taskFail(session)
            return
        
        service_name = host.container
        new_port = []
        if ComputeNetworkTypeEnum.share == host.network_type:
            
            if not host.network:
                
                # calculate new_port
                _current_ports = host.port;      # instance of HostPort
                
                
                _allocate_ports = []
                port_count = len(port)
                if 0 != port_count:   
                    # allocate new port
                    pool_id = host.network_source
                    for index in range(0, port_count, 2):
                        _p_protocol    = port[index]
                        _p_host_port   = port[index + 1]
                        public_port = 0
                        found = False
                        for _curr_host_port in _current_ports:  # instance of HostPort
                            if _curr_host_port.protocol==_p_protocol and _curr_host_port.host_port==_p_host_port:
                                public_port = _curr_host_port.public_port
                                found = True
                                break;
                        if not found:
                            allocated_port_list = self.port_manager.allocatePort(pool_id, host.public_ip, 1)
                            if allocated_port_list is None:
                                self.error("[%08X] <modify_host> modify host fail, insufficient port in port pool '%s' in ip '%s'"%(session.session_id, pool_id, host.public_ip))
                                self.taskFail(session)
                                return
                            public_port = allocated_port_list[0]
                            self.error("[%08X] <modify_host> allocate port '%s:%s' for host '%s'" % (session.session_id, host.public_ip, public_port, host.uuid))
                            _allocate_ports.append(public_port);
                        new_port.extend([_p_protocol, _p_host_port, public_port])
                session._ext_data["allocate_ports"] = _allocate_ports
                        
                        
                # calculate deallocated ports
                _deallocate_ports = []
                for _curr_host_port in _current_ports:  # instance of HostPort
                    _found = False
                    for index in range(0, port_count, 2):
                        _protocal    = port[index]
                        _p_host_port = port[index + 1]
                        if _curr_host_port.protocol==_protocal and _curr_host_port.host_port==_p_host_port:
                            _found = True
                            break;
                    if not _found:
                        _deallocate_ports.append(_curr_host_port.public_port)
                session._ext_data["deallocate_ports"] = _deallocate_ports
                        
                request.setUIntArray(ParamKeyDefine.port, new_port)
            
            else:
                self.warn("[%08X] <modify_host> host '%s' has been attached to vpc network, couldn't modify port(s)"%(session.session_id, host.uuid))
            
        elif ComputeNetworkTypeEnum.private == host.network_type:
            
            if not host.network: 
                # rerange port
                if 0 != len(port):
                    for index in range(0, len(port), 2):
                        proto = port[index]
                        host_port = port[index + 1]
                        new_port.extend([proto, host_port, 0])
                    request.setUIntArray(ParamKeyDefine.port, new_port)
            else:
                self.warn("[%08X] <modify_host> host '%s' has been attached to vpc network, couldn't modify port(s)"%(session.session_id, host.uuid))
            
        self.info("[%08X] <modify_host> request modify host '%s'('%s') to compute node '%s'" % (session.session_id, host.name, host.uuid, service_name))
        
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)

    
    def onModifySuccess(self, msg, session):
        self.clearTimer(session)
        
        _parameter = session._ext_data["parameter"] 
        
        request = session.initial_message
        
        host = self.config_manager.getHost(session.target)
        self.info("[%08X] <modify_host> modify host success, host '%s'('%s')"%(session.session_id, host.name, host.uuid))

        name = request.getString(ParamKeyDefine.name)
        if 0 != len(name):
            host.name = name
            self.info("[%08X] <modify_host> host name changed to '%s'"%(session.session_id, name))
            
        cpu_count = request.getUInt(ParamKeyDefine.cpu_count)
        if 0 != cpu_count:
            host.cpu_count = cpu_count
            self.info("[%08X] <modify_host> vcpu count changed to %d"%(session.session_id, cpu_count))
            
        memory = request.getUInt(ParamKeyDefine.memory)
        if 0 != memory:
            host.memory = memory
            self.info("[%08X] <modify_host> memory changed to %d MiB"%(session.session_id, memory/1048576))
        
        option = _parameter["option"]
        if option != None and len(option) >= 1:
            host.auto_start = True if option[0] > 0 else False# auto_start
            if host.auto_start == True:
                self.info("[%08X] <modify_host> host auto start enabled"%(session.session_id))
            else:
                self.info("[%08X] <modify_host> host auto start disabled"%(session.session_id))
            
        if option != None and len(option) >= 2:
            host.enable_local_backup = EnableLocalBackupEnum.enabled if option[1] > 1 else EnableLocalBackupEnum.disabled
            # enable_local_backup
            if host.enable_local_backup == EnableLocalBackupEnum.disabled:
                self.info("[%08X] <modify_host> host local backup disabled" % (session.session_id))
            else:
                self.info("[%08X] <modify_host> host local backup enabled" % (session.session_id))
        
        if option != None and len(option) >= 3:
            host.enable_usb_ext = EnableUsbExtEnum.enabled if option[2] > 1 else EnableUsbExtEnum.disabled
            # enable_usb_ext
            if host.enable_usb_ext == EnableUsbExtEnum.disabled:
                self.info("[%08X] <modify_host> host usb ext disabled" % (session.session_id))
            else:
                self.info("[%08X] <modify_host> host usb ext enabled" % (session.session_id))
        
        if option != None and len(option) >= 4:
            host.video_type = VideoTypeEnum.h264 if option[3] > 0 else VideoTypeEnum.mjpeg
            if host.video_type == VideoTypeEnum.h264:
                self.info("[%08X] <modify_host> host changes video type to h264" %
                          (session.session_id))
            else:
                self.info("[%08X] <modify_host> host changes video type to mjpeg" %
                          (session.session_id))
            
        display = request.getString(ParamKeyDefine.display)
        if 0 != len(display):
            host.display = display
            self.info("[%08X] <modify_host> display changed to '%s'"%(session.session_id, display))
            
        authentication = request.getString(ParamKeyDefine.authentication)
        if 0 != len(authentication):
            host.authentication = authentication
            self.info("[%08X] <modify_host> authentication changed to '%s'"%(session.session_id, authentication))
            
        network = request.getString(ParamKeyDefine.network)
        if 0 != len(network):
            host.network = network
            self.info("[%08X] <modify_host> network changed to '%s'"%(session.session_id, network))
            
        inbound_bandwidth = request.getUInt(ParamKeyDefine.inbound_bandwidth)
        if 0 != inbound_bandwidth:
            host.inbound_bandwidth = inbound_bandwidth
            self.info("[%08X] <modify_host> inbound bandwidth changed to %d KBps"%(session.session_id, inbound_bandwidth/1024))

        outbound_bandwidth = request.getUInt(ParamKeyDefine.outbound_bandwidth)
        if 0 != outbound_bandwidth:
            host.outbound_bandwidth = outbound_bandwidth
            self.info("[%08X] <modify_host> outbound bandwidth changed to %d KBps"%(session.session_id, outbound_bandwidth/1024))
            
        max_iops = request.getUInt(ParamKeyDefine.io)
        if max_iops != host.max_iops:
            host.max_iops = max_iops
            self.info("[%08X] <modify_host> max iops changed to %d" %
                      (session.session_id, max_iops))
            
        cpu_priority = request.getUInt(ParamKeyDefine.priority)
        if cpu_priority != host.cpu_priority:
            host.cpu_priority = cpu_priority
            self.info("[%08X] <modify_host> cpu priority changed to %d" %
                      (session.session_id, cpu_priority))
       
        ##nat port
        nat_list = msg.getUIntArray(ParamKeyDefine.nat)

        if 0 != (len(nat_list)%4):
            self.warn("[%08X] <modify_host> warning: modify host success, but nat port list is invalid(length %d)"%(session.session_id, len(nat_list)))
        else:
            host.port = []
            for offset in range(0, len(nat_list), 4):
                port = HostPort()
                port.protocol    = nat_list[offset]
                port.server_port = nat_list[offset + 1]
                port.host_port   = nat_list[offset + 2]
                port.public_port = nat_list[offset + 3]
                host.port.append(port)
                
                
        if ComputeNetworkTypeEnum.share == host.network_type:
            forwarder_id = host.forwarder
            pool_id      = host.network_source
            forwarder = self.forwarder_manager.get(forwarder_id)
            
            _deallocate_ports = session._ext_data.get("deallocate_ports", None)
            if _deallocate_ports!=None:
                self.info("[%08X] <modify_host> deallocate public port: %s"%(session.session_id, _deallocate_ports))
                self.port_manager.deallocate(pool_id, host.public_ip, _deallocate_ports)
            
            # new_hostForwarder = HostForwarder()                
            forwarder_dict = {}
            forwarder_dict["port"] = []
            for allocated_port in host.port:
                port = ForwarderPort()
                port.server_port = allocated_port.server_port
                port.host_port   = allocated_port.host_port
                port.public_port = allocated_port.public_port
                forwarder_dict["port"].append(port)
            self.forwarder_manager.modifyByDict(forwarder.uuid, forwarder_dict)
            # forwarder.port = forwarder_dict.port
            
            #
            remove_request = getRequest(RequestDefine.remove_forwarder)
            remove_request.session = session.session_id
            remove_request.setString(ParamKeyDefine.uuid, forwarder_id)
            
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            if default_ir is None:
                self.error("[%08X] <modify_host> modify host success, but no intelligent router actived for share host"%(session.session_id))
                self.taskFail(session)
                return
            
            self.sendMessage(remove_request, default_ir)
            self.setTimer(session, self.operate_timeout)
            session.target = forwarder_id
            self.info("[%08X] <modify_host> request remove forwarder '%s' to intelligent router '%s' for modify..."%(
                                                                                                      session.session_id, forwarder_id, default_ir))
            return
            
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()


    def onModifyFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <modify_host> modify host fail, id '%s'"% (session.session_id, session.target))
        _allocate_ports = session._ext_data["allocate_ports"]
        host = self.config_manager.getHost(session.target)
        if ComputeNetworkTypeEnum.share == host.network_type:
            self.info("[%08X] <modify_host> deallocate allocated port: %s"% (session.session_id, _allocate_ports))
            self.port_manager.deallocate(host.network_source, host.public_ip, _allocate_ports)
        self.taskFail(session)
        
        
    def onModifyTimeout(self, msg, session):
        self.error("[%08X] <modify_host> modify host timeout, id '%s'"% (session.session_id, session.target))
        _allocate_ports = session._ext_data["allocate_ports"]
        host = self.config_manager.getHost(session.target)
        if ComputeNetworkTypeEnum.share == host.network_type:
            self.info("[%08X] <modify_host> deallocate allocated port: %s"% (session.session_id, _allocate_ports))
            self.port_manager.deallocate(host.network_source, host.public_ip, _allocate_ports)
        self.taskFail(session)


    def onRemoveSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <modify_host> remove forwarder in intelligent router success, forwarder id '%s'"%(session.session_id, session.target))
        
        forwarder = self.forwarder_manager.get(session.target)
        
        default_ir = self.message_handler.getDefaultIntelligentRouter()
        if default_ir is None:
            self.error("[%08X] <modify_host> no intelligent router actived for add forwarder"%(session.session_id))
            self.taskFail(session)
            return
        
        request = getRequest(RequestDefine.add_forwarder)
        request.session = session.session_id
        request.setString(ParamKeyDefine.uuid,     forwarder.uuid)
        request.setUInt(ParamKeyDefine.type,       forwarder.type)
        request.setString(ParamKeyDefine.host,     forwarder.host_id)
        request.setString(ParamKeyDefine.name,     forwarder.host_name)
        request.setUIntArray(ParamKeyDefine.range, forwarder.output_port_range)
        request.setUInt(ParamKeyDefine.status,     1 if (forwarder.enable==True) else 0)
        
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
        self.info("[%08X] <modify_host> request add forwarder '%s' to intelligent router '%s' for modify..."%(
                                                                                               session.session_id, forwarder.uuid, default_ir))
        

                    

    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <modify_host> remove forwarder fail, forwarder id '%s'"%(
                                                                                    session.session_id, session.target))
        self.taskFail(session)
    
    def onRemoveTimeout(self, msg, session):
        self.error("[%08X] <modify_host> remove forwarder timeout, forwarder id '%s'"%(
                                                                                       session.session_id, session.target))
        self.taskFail(session)





    def onAddSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <modify_host> add forwarder in intelligent router success, forwarder id '%s'"%(
                                                                                          session.session_id, session.target))
        response = getResponse(RequestDefine.modify_host)
        response.success = True
        forwarder = self.forwarder_manager.get(session.target)

        
        host = self.config_manager.getHost(forwarder.host_id)
        port = []
        if 0 != host.port:
            for allocated_port in host.port:
                port.extend([allocated_port.protocol,
                             allocated_port.server_port,
                             allocated_port.host_port,
                             allocated_port.public_port])
        response.setUIntArray(ParamKeyDefine.nat, port)
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
                    

    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <modify_host> add forwarder fail, forwarder id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)
                    

    def onAddTimeout(self, msg, session):
        self.info("[%08X] <modify_host> add forwarder timeout, forwarder id '%s'"%(
            session.session_id, session.target))
        self.taskFail(session)

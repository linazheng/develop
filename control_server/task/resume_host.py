#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from host_info import *
from host_forwarder import HostForwarder, ForwarderTypeEnum, ForwarderPort

class ResumeHostTask(BaseTask):
    
    operate_timeout = 5
    
    def __init__(self, task_type, message_handler, config_manager, compute_pool_manager, address_manager, port_manager, forwarder_manager):
        self.config_manager       = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.address_manager      = address_manager
        self.port_manager         = port_manager
        self.forwarder_manager    = forwarder_manager
        logger_name = "task.resume_host"
        BaseTask.__init__(self, task_type, RequestDefine.invalid, message_handler, logger_name)

        ##state rule define, state id from 1
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host, result_success, self.onQueryHostSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host, result_fail,    self.onQueryHostFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,      result_any,     self.onQueryHostTimeout)
                

    def invokeSession(self, session):
        """
        task start, must override
        """
        session.target  = session.initial_message.getString(ParamKeyDefine.target)
        request         = getRequest(RequestDefine.query_host)
        request.session = session.session_id
        
        self.sendMessage(request, session.target)
        self.setTimer(session, self.operate_timeout)
        
        self.info("[%08X]resume host, request query host to '%s'..."%(session.session_id, session.target))

    def onQueryHostSuccess(self, response, session):
        self.clearTimer(session)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        count = len(uuid)
        
        if 0 == count:
            self.info("[%08X]query host success, but no host available"%(session.session_id))
            session.finish()
            return

        is_node_attached, pool_id = self.compute_pool_manager.searchResource(session.target)
        if not is_node_attached:
            self.error("[%08X]query host success, but compute node not in pool"%(session.session_id))
            session.finish()
            return
        
        resource_node = self.compute_pool_manager.getResource(pool_id, session.target)
            
        name        = response.getStringArray(ParamKeyDefine.name)
        cpu_count   = response.getUIntArray(ParamKeyDefine.cpu_count)
        memory      = response.getUIntArray(ParamKeyDefine.memory)
        option      = response.getUIntArrayArray(ParamKeyDefine.option)
        disk_volume = response.getUIntArrayArray(ParamKeyDefine.disk_volume)
        port        = response.getUIntArrayArray(ParamKeyDefine.port)

        user           = response.getStringArray(ParamKeyDefine.user)
        group          = response.getStringArray(ParamKeyDefine.group)
        display        = response.getStringArray(ParamKeyDefine.display)
        authentication = response.getStringArray(ParamKeyDefine.authentication)
        network        = response.getStringArray(ParamKeyDefine.network)

        inbound_bandwidth  = response.getUIntArray(ParamKeyDefine.inbound_bandwidth)
        outbound_bandwidth = response.getUIntArray(ParamKeyDefine.outbound_bandwidth)
        
        ip           = response.getStringArrayArray(ParamKeyDefine.ip)
        display_port = response.getUIntArrayArray(ParamKeyDefine.display_port)

        forwarder      = response.getStringArray(ParamKeyDefine.forward)
        network_type   = response.getUIntArray(ParamKeyDefine.network_type)
        network_source = response.getStringArray(ParamKeyDefine.network_source)
        disk_type      = response.getUIntArray(ParamKeyDefine.disk_type)
        disk_source    = response.getStringArray(ParamKeyDefine.disk_source)

        host_list = []
        for i in range(count):
            if not self.config_manager.containsHost(uuid[i]):
                ##need resumed
                host = HostInfo()
                host.container = session.target
                host.uuid      = uuid[i]
                host.name      = name[i]
                host.cpu_count = cpu_count[i]
                host.memory    = memory[i]
                
                if 1 == option[i][0]:
                    host.auto_start = True
                    
                host.data_disk_count = option[i][1]
                host.disk_volume     = disk_volume[i]
                
                ##port
                if 0 != len(port[i]):
                    for offset in range(0, len(port[i]), 4):
                        allocate_port = HostPort()
                        allocate_port.protocol    = port[i][offset]
                        allocate_port.server_port = port[i][offset + 1]
                        allocate_port.host_port   = port[i][offset + 2]
                        allocate_port.public_port = port[i][offset + 3]                    
                        host.port.append(allocate_port)

                host.user           = user[i]
                host.group          = group[i]
                host.display        = display[i]
                host.authentication = authentication[i]
                host.network        = network[i]

                host.inbound_bandwidth  = inbound_bandwidth[i]
                host.outbound_bandwidth = outbound_bandwidth[i]

                host.server_ip = ip[i][0]
                host.public_ip = ip[i][1]

                host.server_port    = display_port[i][0]
                host.public_port    = display_port[i][1]
                host.forwarder      = forwarder[i]
                host.network_type   = network_type[i]
                host.network_source = network_source[i]
                host.disk_type      = disk_type[i]
                host.disk_source    = disk_source[i]        
                        
                ##resume compute resource
                if not resource_node.containsHost(host.uuid):
                    host.pool = pool_id
                    resource_node.addHost(host.uuid)
                elif host.pool == "":
                    host.pool = pool_id
                    
                ##resume network config
                if NetworkTypeEnum.mono == host.network_type:
                    ##mono network
                    if self.address_manager.containsPool(host.network_source):
                        address_pool = self.address_manager.getPool(host.network_source)
                        if address_pool.setAllocated(host.public_ip):
                            self.info("[%08X]resume public ip '%s' into address pool '%s'"%(session.session_id, 
                                                                                            host.public_ip, 
                                                                                            host.network_source))
                elif NetworkTypeEnum.share == host.network_type:
                    public_port = []
                    for port in host.port:
                        public_port.append(port.public_port)
                    if self.pool_manager.containsPool(host.network_source):
                        port_pool = self.pool_manager.getPool(host.network_source)
                        if port_pool.setAllocated(host.public_ip, public_port):
                            self.info("[%08X] <resume_host> resume %d port(s) with public ip '%s' into address pool '%s'"%(session.session_id, 
                                                                                                                           len(public_port), 
                                                                                                                           host.public_ip, 
                                                                                                                           host.network_source))                            

                self.info("[%08X]resume host '%s'('%s') in compute node '%s'"%(session.session_id, 
                                                                               host.name, 
                                                                               host.uuid, 
                                                                               session.target))

                ##resume forwarder
                if (0 != len(host.forwarder)) and (not self.forwarder_manager.contains(host.forwarder)):
                    forwarder = HostForwarder()
                    forwarder.uuid = host.forwarder
                    
                    if 2 == host.network_type:
                        ##share
                        forwarder.type = ForwarderTypeEnum.share
                        
                    forwarder.host_id        = host.uuid
                    forwarder.host_name      = host.name
                    forwarder.public_ip      = [host.public_ip]
                    forwarder.public_monitor = host.public_port                    
                    forwarder.server_ip      = host.server_ip
                    forwarder.server_monitor = host.server_port
                    
                    if 0 != len(host.port):
                        for allocated_port in host.port:
                            forward_port = ForwarderPort()
                            forward_port.server_port = allocated_port.server_port
                            forward_port.host_port   = allocated_port.host_port
                            forward_port.public_port = allocated_port.public_port
                            forwarder.port.append(forward_port)
                            
                    if self.forwarder_manager.create(forwarder):
                        self.info("[%08X]forwarder '%s' resumed for host '%s'"%(session.session_id, 
                                                                                forwarder.uuid, 
                                                                                host.name))
                host_list.append(host)

        count = len(host_list)
        
        if 0 == count:
            self.warn("[%08X]query host success, but no host resumed"%(session.session_id))
            session.finish()
            return
        
        self.compute_pool_manager.savePoolResource(pool_id, session.target)
        for host in host_list:
            self.config_manager.addHost(host)
            
        self.info("[%08X] resume host success, %d host(s) resumed in compute node '%s'"%(session.session_id, 
                                                                                                       count, 
                                                                                                       session.target))
        session.finish()
        return
        
    def onQueryHostFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query host fail, compute node '%s'"%(session.session_id, 
                                                              session.target))
        session.finish()

    def onQueryHostTimeout(self, response, session):
        self.info("[%08X]query host timeout, compute node '%s'"%(session.session_id, 
                                                                 session.target))
        session.finish()

    

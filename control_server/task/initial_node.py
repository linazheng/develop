#!/usr/bin/python

from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from host_info import *
from host_forwarder import *

class InitialNodeTask(BaseTask):
    
    operate_timeout = 5
    interval = 10##10s
##    ##for test
##    lost_check_interval = 20##5 min
    lost_check_interval = 60*5##5 min
    found_expire = 2
    lost_expire = 4##5*4 = 20min
    
    def __init__(self, task_type, message_handler, config_manager, compute_pool_manager, address_manager, port_manager, forwarder_manager, expire_manager):
        self.config_manager       = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.address_manager      = address_manager
        self.port_manager         = port_manager
        self.forwarder_manager    = forwarder_manager
        self.expire_manager       = expire_manager
        
        logger_name = "task.initial_node"
        
        BaseTask.__init__(self, task_type, RequestDefine.invalid, message_handler, logger_name)

        ##state rule define, state id from 1
        stObserve = 2
        stCheck = 3
        self.addState(stObserve)
        self.addState(stCheck)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host, result_success, self.onQueryHostSuccess, stObserve)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host, result_fail,    self.onQueryHostFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,      result_any,     self.onQueryHostTimeout)
                
        # stObserve
        self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.timeout, result_any, self.onCheck, stCheck)
        
        # stCheck
        self.addTransferRule(stCheck, AppMessage.RESPONSE, RequestDefine.query_host, result_success, self.onCheckSuccess, stObserve)
        self.addTransferRule(stCheck, AppMessage.RESPONSE, RequestDefine.query_host, result_fail,    self.onCheckFail,    stObserve)
        self.addTransferRule(stCheck, AppMessage.EVENT,    EventDefine.timeout,      result_any,     self.onCheckTimeout, stObserve)
        

    def invokeSession(self, session):
        """
        task start, must override
        """
        session._ext_data = {}
        
        node_client_name = getString(session.initial_message, ParamKeyDefine.target)
        session._ext_data["node_client_name"] = node_client_name
        
        request = getRequest(RequestDefine.query_host)
        request.session = session.session_id
        self.sendMessage(request, node_client_name)
        self.setTimer(session, self.operate_timeout)
        self.info("[%08X] <initial_node> compute node initialed, request query host to '%s'..." % (session.session_id, node_client_name))


    # self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_host, result_success, self.onQueryHostSuccess, stObserve)
    def onQueryHostSuccess(self, response, session):
        self.clearTimer(session)
        
        node_client_name = session._ext_data["node_client_name"]
        host_list = self.parseHostFromMessage(response, session, node_client_name)
        
        count = len(host_list)
        if 0 == count:
            self.info("[%08X] <initial_node> query host success, but no host available" % (session.session_id))
            
        for host in host_list:
            if host.forwarder:
                forwarder = self.forwarder_manager.get(host.forwarder)
                if not forwarder:
                    self.warn("[%08X] <initial_node> forwarder '%s' not found for host '%s(%s)'" % (session.session_id, host.forwarder, host.name, host.uuid))
                else:
                    forwarder.enable = True
                    
        self.forwarder_manager.updateTotalCRC();
        self.forwarder_manager.setSaveFlag();
            
        pool_available, pool_id = self.compute_pool_manager.searchResource(node_client_name)
        resumed_count = 0
        removed_count = 0
        
        if pool_available:
            resource_node = self.compute_pool_manager.getResource(pool_id, node_client_name)
            
            ##check lost
            remote_id_list = []
            for host in host_list:
                remote_id_list.append(host.uuid)
            
            remove_list = []
            for host_id in resource_node.allocated:
                if host_id not in remote_id_list:
                    ##lost                    
                    removed_count += 1
                    remove_list.append(host_id)
                    if self.config_manager.containsHost(host_id):
                        ##clear resource
                        host = self.config_manager.getHost(host_id)
                        self.releaseHostResource(host, session)
                        self.config_manager.removeHost(host_id)
                        
            if 0 != len(remove_list):
                for host_id in remove_list:
                    resource_node.removeHost(host_id)
                    self.info("[%08X] <initial_node> remove invalid host '%s' from compute node '%s'"%(
                                                                                       session.session_id, host_id, node_client_name))

        for host in host_list:
            ##if need resume
            if pool_available:
                if not resource_node.containsHost(host.uuid):
                    host.pool = pool_id
                    resource_node.addHost(host.uuid)
                    resumed_count += 1
                    self.info("[%08X] <initial_node> resume host '%s'('%s') into compute node '%s'"%(
                                                                                     session.session_id, host.name, host.uuid, node_client_name))
                elif host.pool == "":
                    host.pool = pool_id
            ##resume resource with host
            self.resumeHostResource(host, session)
            
        if (0 != removed_count) or (0 != resumed_count):
            ##save resumed
            self.compute_pool_manager.savePoolResource(pool_id, node_client_name)      
                
        #---------------------          
                
        self.config_manager.loadHosts(node_client_name, host_list)
        self.info("[%08X] <initial_node> query host success, %d host(s) in compute node '%s'"%(session.session_id, count, node_client_name))
            
        ##start check
        self.expire_manager.start(node_client_name)
        self.setLoopTimer(session, self.interval)
        
    def onQueryHostFail(self, response, session):
        self.clearTimer(session)
        node_client_name = session._ext_data["node_client_name"]
        self.error("[%08X] <initial_node> query host fail, compute node '%s'"%(session.session_id, node_client_name))
        session.finish()

    def onQueryHostTimeout(self, response, session):
        node_client_name = session._ext_data["node_client_name"]
        self.error("[%08X] <initial_node> query host timeout, compute node '%s'"%(session.session_id, node_client_name))
        session.finish()

    # self.addTransferRule(stObserve, AppMessage.EVENT, EventDefine.timeout, result_any, self.onCheck, stCheck)
    def onCheck(self, event, session):
        node_client_name = session._ext_data["node_client_name"]
        request = getRequest(RequestDefine.query_host)
        request.session = session.session_id
        self.sendMessage(request, node_client_name)
        
        
    # self.addTransferRule(stCheck, AppMessage.RESPONSE, RequestDefine.query_host, result_success, self.onCheckSuccess, stObserve)
    def onCheckSuccess(self, response, session):
        node_client_name = session._ext_data["node_client_name"]
        host_list = self.parseHostFromMessage(response, session, node_client_name)
        
        pool_available, pool_id = self.compute_pool_manager.searchResource(node_client_name)
        
        id_list    = []
        found_list = []
#         host_map   = {}
        
        session.counter = (session.counter +  1) % (self.lost_check_interval * self.interval)
        resource_modifed = False
        
        if pool_available:
            resource_node = self.compute_pool_manager.getResource(pool_id, node_client_name)
        
        for host in host_list:
            id_list.append(host.uuid)
#             host_map[host.uuid] = host
            
            ##check found
            if not self.config_manager.containsHost(host.uuid):
                
                ##new host id
                if not self.expire_manager.isFound(node_client_name, host.uuid, self.found_expire):
                    
                    ##wait further confirm
                    found_list.append(host.uuid)
                    self.info("[%08X] <initial_node> new host '%s' found"%(session.session_id, host.uuid))
                    continue
                
                ##new host found confirmed,begin resume
                self.info("[%08X] <initial_node> new host '%s' confirmed"%(session.session_id, host.uuid))
                self.config_manager.addHost(host)
                
                if pool_available:
                    if not resource_node.containsHost(host.uuid):
                        host.pool = pool_id
                        resource_node.addHost(host.uuid)
                        if not resource_modifed:
                            resource_modifed = True
                        self.info("[%08X] <initial_node> resume host '%s'('%s') into compute node '%s'"%(
                                                                                         session.session_id, host.name, host.uuid, node_client_name))
            else:
                self.config_manager.updateHost(host)
            ##force resume
            self.resumeHostResource(host, session)

        self.expire_manager.updateFound(node_client_name, found_list) 
        ##check lost
        if 0 == (session.counter%self.lost_check_interval):            
            if pool_available:
                lost_list = []
                remove_list = []
                for host_id in resource_node.allocated:
                    if host_id not in id_list:
                        ##maybe lost
                        if not self.expire_manager.isLost(node_client_name, host_id, self.lost_expire):
                            lost_list.append(host_id)
                            self.info("[%08X] <initial_node> lost host '%s' found"%(
                                                                    session.session_id, host_id))
                            continue
                        ##lost confirmed
                        self.info("[%08X] <initial_node> lost host '%s' confirmed"%(
                                                                    session.session_id, host_id))
                        host = self.config_manager.getHost(host_id)
                        self.releaseHostResource(host, session)
                        self.config_manager.removeHost(host_id)
                        remove_list.append(host_id)
                self.expire_manager.updateLost(node_client_name, lost_list)
                if 0 != len(remove_list):
                    if not resource_modifed:
                            resource_modifed = True
                    for host_id in remove_list:
                        resource_node.removeHost(host_id)
                        self.info("[%08X] <initial_node> remove host '%s' from compute node '%s'"%(session.session_id, host_id, node_client_name))
                        
        if pool_available and resource_modifed:
            self.compute_pool_manager.savePoolResource(pool_id, node_client_name)                            

    def onCheckFail(self, response, session):
        node_client_name = session._ext_data["node_client_name"]
        self.warn("[%08X] <initial_node> check resource fail, compute node '%s'"%(session.session_id, node_client_name))
        
    def onCheckTimeout(self, event, session):
        node_client_name = session._ext_data["node_client_name"]
        self.warn("[%08X] <initial_node> check resource timeout, compute node '%s'"%(session.session_id, node_client_name))

    def parseHostFromMessage(self, response, session, node_name):
        result = []
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        count = len(uuid)
        if 0 == count:
            return result
                        
        name        = response.getStringArray(ParamKeyDefine.name)
        cpu_count   = response.getUIntArray(ParamKeyDefine.cpu_count)
        memory      = response.getUIntArray(ParamKeyDefine.memory)
        option      = response.getUIntArrayArray(ParamKeyDefine.option)
        disk_volume = response.getUIntArrayArray(ParamKeyDefine.disk_volume)
        port        = response.getStringArrayArray(ParamKeyDefine.port)

        user           = response.getStringArray(ParamKeyDefine.user)
        group          = response.getStringArray(ParamKeyDefine.group)
        display        = response.getStringArray(ParamKeyDefine.display)
        authentication = response.getStringArray(ParamKeyDefine.authentication)
        network        = response.getStringArray(ParamKeyDefine.network)

        inbound_bandwidth  = response.getUIntArray(ParamKeyDefine.inbound_bandwidth)
        outbound_bandwidth = response.getUIntArray(ParamKeyDefine.outbound_bandwidth)
        max_iops           = response.getUIntArray(ParamKeyDefine.io)
        cpu_priority       = response.getUIntArray(ParamKeyDefine.priority)
        
#         vpc_network        = response.getStringArray(ParamKeyDefine.vpc_network)
        vpc_ip = response.getStringArray(ParamKeyDefine.network_address)  # vpc_ip             = response.getStringArray(ParamKeyDefine.vpc_ip)

        ip             = response.getStringArrayArray(ParamKeyDefine.ip)
        display_port   = response.getUIntArrayArray(ParamKeyDefine.display_port)
        forwarder      = response.getStringArray(ParamKeyDefine.forward)
        network_type   = response.getUIntArray(ParamKeyDefine.network_type)
        network_source = response.getStringArray(ParamKeyDefine.network_source)
        disk_type      = response.getUIntArray(ParamKeyDefine.disk_type)
        disk_source    = response.getStringArray(ParamKeyDefine.disk_source)
        
        for i in range(count):
            host = HostInfo()
            host.container = node_name
            host.uuid      = uuid[i]
            host.name      = name[i]
            host.cpu_count = cpu_count[i]
            host.memory    = memory[i]
            
            host_option = option[i]
            if len(host_option) >= 1 and host_option[0] > 0:
                host.auto_start = True
            
            if len(host_option) >= 2 and host_option[1] > 0:
                host.data_disk_count = host_option[1]
            
            if len(host_option) >= 3 and host_option[2] > 0 :
                host.enable_local_backup = EnableLocalBackupEnum.enabled
                
            if len(host_option) >= 4 and host_option[3] > 0:
                host.enable_usb_ext = EnableUsbExtEnum.enabled
                
            if len(host_option) >= 5 and host_option[4] > 0:
                host.thin_provisioning = ThinProvisioningModeEnum.enabled
                
            if len(host_option) >= 6 and host_option[5] > 0:
                host.backing_image = BackingImageModeEnum.enabled
                
            if len(host_option) >= 7 and host_option[6] > 0:
                host.video_type = VideoTypeEnum.h264
                    
            host.disk_volume     = disk_volume[i]
            
            ##port
            if 0 != len(port[i]):
                for offset in range(0, len(port[i]), 5):
                    allocate_port = HostPort()
                    allocate_port.protocol    = int(port[i][offset])
                    allocate_port.server_port = int(port[i][offset + 1])
                    allocate_port.host_port   = int(port[i][offset + 2])
                    allocate_port.public_ip   = str(port[i][offset + 3])  
                    allocate_port.public_port = int(port[i][offset + 4])                    
                    host.port.append(allocate_port)

            host.user           = user[i]
            host.group          = group[i]
            host.display        = display[i]
            host.authentication = authentication[i]
            host.network        = network[i]

            host.inbound_bandwidth  = inbound_bandwidth[i]
            host.outbound_bandwidth = outbound_bandwidth[i]
            if max_iops != None and len(max_iops) > i:
                host.max_iops = max_iops[i]
            
            if cpu_priority != None and len(cpu_priority) > i:
                host.cpu_priority = cpu_priority[i]
            
#             host.vpc_network = vpc_network[i]
            host.vpc_ip      = vpc_ip[i]
            
            host.server_ip = ip[i][0]
            host.public_ip = ip[i][1]

            host.server_port    = display_port[i][0]
            host.public_port    = display_port[i][1]
            host.forwarder      = forwarder[i]
            host.network_type   = network_type[i]
            host.network_source = network_source[i]
            host.disk_type      = disk_type[i]
            host.disk_source    = disk_source[i]                

            result.append(host)
        return result
        
        
    def resumeHostResource(self, host, session):
        ##resume network config
        if NetworkTypeEnum.mono == host.network_type:
            ##mono network
            if self.address_manager.containsPool(host.network_source):
                address_pool = self.address_manager.getPool(host.network_source)
                if host.public_ip:
                    if address_pool.setAllocated(host.public_ip):
                        self.info("[%08X] <initial_node> resume public ip '%s' into address pool '%s'"%(session.session_id, 
                                                                                    host.public_ip, 
                                                                                    host.network_source))
                    
        elif NetworkTypeEnum.share == host.network_type:
            if not host.network:
                public_port = []
                
                for port in host.port:
                    public_port.append(port.public_port)
                    
                if self.port_manager.containsPool(host.network_source):
                    port_pool = self.port_manager.getPool(host.network_source)      # instance of PortPool
                    if not port_pool.isAllAllocated(host.public_ip, public_port):
                        port_pool.setAllocated(host.public_ip, public_port)
                        self.info("[%08X] <initial_node> resume %d port(s) '%s' with public ip '%s' into address pool '%s'"%(session.session_id, 
                                                                                                                             len(public_port),
                                                                                                                             public_port,
                                                                                                                             host.public_ip, 
                                                                                                                             host.network_source))                            
        ##resume forwarder
        if 0 != len(host.forwarder):
            resumed_forwarder = HostForwarder()
            resumed_forwarder.uuid = host.forwarder
            if 2 == host.network_type:
                ##share
                resumed_forwarder.type = ForwarderTypeEnum.share
            resumed_forwarder.host_id = host.uuid
            resumed_forwarder.host_name = host.name
            resumed_forwarder.public_ip = [host.public_ip]
            resumed_forwarder.public_monitor = host.public_port                    
            resumed_forwarder.server_ip = host.server_ip
            resumed_forwarder.server_monitor = host.server_port
            if 0 != len(host.port):
                for allocated_port in host.port:
                    forward_port = ForwarderPort()
                    forward_port.server_port = allocated_port.server_port
                    forward_port.host_port = allocated_port.host_port
                    forward_port.public_port = allocated_port.public_port
                    resumed_forwarder.port.append(forward_port)
            if not self.forwarder_manager.contains(host.forwarder):
                if self.forwarder_manager.create(resumed_forwarder):
                    self.info("[%08X] <initial_node> create forwarder '%s' for host '%s'"%(
                                                                           session.session_id, resumed_forwarder.uuid, host.name))
                else:
                    self.warn("[%08X] <initial_node> create forwarder '%s' for host '%s' fail"%(
                                                                                session.session_id, resumed_forwarder.uuid, host.name))
            elif self.forwarder_manager.isInvalid(resumed_forwarder.uuid):
                ##need modify invalid host id
                if self.forwarder_manager.modify(resumed_forwarder.uuid, resumed_forwarder):
                    self.info("[%08X] <initial_node> modify forwarder '%s' for host '%s'"%(
                                                                           session.session_id, resumed_forwarder.uuid, host.name))
                else:
                    self.warn("[%08X] <initial_node> modify forwarder '%s' for host '%s' fail"%(
                                                                                session.session_id, resumed_forwarder.uuid, host.name))
        
    def releaseHostResource(self, host, session):
        ##release network config
        if NetworkTypeEnum.mono == host.network_type:
            ##mono network
            if self.address_manager.containsPool(host.network_source):
                address_pool = self.address_manager.getPool(host.network_source)
                if address_pool.setUnallocated(host.public_ip):
                    self.info("[%08X] <initial_node> release public ip '%s' back to address pool '%s'"%(
                                                                                        session.session_id, host.public_ip, host.network_source))
        elif NetworkTypeEnum.share == host.network_type:
            public_port = []
            for port in host.port:
                public_port.append(port.public_port)
            if self.port_manager.containsPool(host.network_source):
                port_pool = self.port_manager.getPool(host.network_source)
                if port_pool.setUnallocated(host.public_ip, public_port):
                    self.info("[%08X] <initial_node> release %d port(s) with public ip '%s' back to address pool '%s'"%(
                                                                                                        session.session_id, len(public_port), host.public_ip, host.network_source))                            
        ##resume forwarder
        if (0 != len(host.forwarder)):
            if self.forwarder_manager.contains(host.forwarder):
                self.forwarder_manager.delete(host.forwarder)
                self.info("[%08X] <initial_node> forwarder '%s' removed for host '%s'"%(
                                                                        session.session_id, host.forwarder, host.name))   

    def onTerminate(self, session):
        """
        overridable
        """
        node_client_name = session._ext_data["node_client_name"]
        self.clearTimer(session)
        self.expire_manager.finish(node_client_name)
        self.info("[%08X] <initial_node> terminated"%(session.session_id))

#!/usr/bin/python
from host_requirement import *
from resource_status_enum import *
import math
from common import dict_util
from host_forwarder import HostForwarder, ForwarderTypeEnum, ForwarderPort
from compute_pool import ComputeNetworkTypeEnum, ThinProvisioningModeEnum,\
    BackingImageModeEnum
from host_info import HostInfo, HostPort, EnableLocalBackupEnum, VideoTypeEnum,\
    DiskTypeEnum
from default_compute_selector import DefaultComputeSelector
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, EventDefine, ParamKeyDefine,\
    getRequest, getEvent, getResponse
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage
from compute_pool import ComputeStorageTypeEnum
from disk_image import DiskImageFileTypeEnum
from host_info import EnableUsbExtEnum

class CreateHostTask(BaseTask):
    
    operate_timeout = 60
    notify_interval = 2
    max_timeout = 90            ##2s*90=max 180s
    
    def __init__(self, task_type, messsage_handler,
                 status_manager, config_manager,
                 compute_pool_manager, image_manager,
                 address_manager, port_manager,
                 forwarder_manager):
        
        self.status_manager       = status_manager
        self.config_manager       = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.image_manager        = image_manager
        self.address_manager      = address_manager
        self.port_manager         = port_manager
        self.forwarder_manager    = forwarder_manager
        logger_name = "task.create_host"
        BaseTask.__init__(self, task_type, RequestDefine.create_host, messsage_handler, logger_name)

        ##state rule define, state id from 1
        stCreateHost = 2
        stAddForwarder = 3
        self.addState(stCreateHost)
        self.addState(stAddForwarder)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.ack,           result_success, self.onCreateStarted, stCreateHost)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_host, result_success, self.onCreateSuccess, stAddForwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_host, result_fail,    self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,       result_any,     self.onCreateTimeout, state_initial)
        
        # stCreateHost
        self.addTransferRule(stCreateHost, AppMessage.RESPONSE, RequestDefine.create_host, result_success, self.onCreateSuccess, stAddForwarder)
        self.addTransferRule(stCreateHost, AppMessage.RESPONSE, RequestDefine.create_host, result_fail,    self.onCreateFail)
        self.addTransferRule(stCreateHost, AppMessage.EVENT,    EventDefine.report,        result_any,     self.onCreateReport,  stCreateHost)
        self.addTransferRule(stCreateHost, AppMessage.EVENT,    EventDefine.timeout,       result_any,     self.onCreateTimeout, stCreateHost)

        # stAddForwarder
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddSuccess)
        self.addTransferRule(stAddForwarder, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail,    self.onAddFail)
        self.addTransferRule(stAddForwarder, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onAddTimeout)        
    
    
    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        
        session._ext_data = {};
        
        _parameter = {}
        _parameter["host_name"]   = request.getString(ParamKeyDefine.name)
        _parameter["option"]      = request.getUIntArray(ParamKeyDefine.option)
        _parameter["image_id"]    = request.getString(ParamKeyDefine.image)
        _parameter["pool_id"]     = request.getString(ParamKeyDefine.pool)
        _parameter["cpu_count"]   = request.getUInt(ParamKeyDefine.cpu_count)
        _parameter["memory"]      = request.getUInt(ParamKeyDefine.memory)
        _parameter["disk_volume"] = request.getUIntArray(ParamKeyDefine.disk_volume)
        _parameter["port"]        = request.getUIntArray(ParamKeyDefine.port)
        
        host_name = request.getString(ParamKeyDefine.name)
        self.info("[%08X] <create_host> receive create host request from '%s', host name '%s', parameter: %s" % 
                  (session.session_id, session.request_module, host_name, dict_util.toDictionary(_parameter)))
        
        option = _parameter["option"]        
        if option != None and len(option) >= 1 and option[0] > 0:
            use_image = 1
        else:
            use_image = 0
            
        if option != None and len(option) >= 2 and option[1] >= 0:
            data_disk_count = option[1]
        else:
            data_disk_count = 0
            
        if option != None and len(option) >= 3 and option[2] > 0:
            auto_start = 1
        else:
            auto_start = 0
            
        if option != None and len(option) >= 4 and option[3] > 0:
            enable_local_backup = EnableLocalBackupEnum.enabled
        else:
            enable_local_backup = EnableLocalBackupEnum.disabled
            
        if option != None and len(option) >= 5 and option[4] > 0:
            enable_usb_extention = EnableUsbExtEnum.enabled
        else:
            enable_usb_extention = EnableUsbExtEnum.disabled
            
        if option != None and len(option) >= 6 and option[5] > 0:
            video_type = VideoTypeEnum.h264
        else:
            video_type = VideoTypeEnum.mjpeg
            
        pool_id = request.getString(ParamKeyDefine.pool)
        if not self.compute_pool_manager.containsPool(pool_id):
            self.error("[%08X] <create_host> create host fail, invalid compute pool id '%s'"%
                       (session.session_id, pool_id))
            self.taskFail(session)
            return
        
        compute_pool = self.compute_pool_manager.getPool(pool_id)
        
        if compute_pool.disk_type == ComputeStorageTypeEnum.nas:
            request.setString(ParamKeyDefine.path, "host_file/%s" % pool_id)
        
        ##check image
        if use_image == 1:            
            image_id = request.getString(ParamKeyDefine.image)            
            if not self.image_manager.containsImage(image_id):
                self.error("[%08X] <create_host> create host fail, invalid image id '%s'"%
                           (session.session_id, image_id))
                self.taskFail(session)
                return       
                 
            image = self.image_manager.getImage(image_id)
            
            if compute_pool.disk_type != image.disk_type:
                self.error("[%08X] <create_host> fail, disk type not match, compute pool '%s/%d', disk image '%s/%d'"%
                           (session.session_id, compute_pool.name, compute_pool.disk_type, image.name, image.disk_type))
                self.taskFail(session)
                return
            
            if compute_pool.thin_provisioning==ThinProvisioningModeEnum.enabled and image.file_type!=DiskImageFileTypeEnum.qcow2:
                self.error("[%08X] <create_host> fail, disk image file type must be qcow2, but now file_type is '%s'" % (session.session_id, image.file_type))
                self.taskFail(session)
                return                
            
            if compute_pool.backing_image==BackingImageModeEnum.enabled:
                if compute_pool.thin_provisioning!=ThinProvisioningModeEnum.enabled:
                    self.error("[%08X] <create_host> fail, backing_image enabled, but thin_provisioning disabled")
                    self.taskFail(session)
                    return   
                if compute_pool.disk_type!=ComputeStorageTypeEnum.nas:
                    self.error("[%08X] <create_host> fail, backing_image enabled, but disk type is not nas")
                    self.taskFail(session)
                    return   
            
            request.setString(ParamKeyDefine.target, image.container)
            if compute_pool.disk_type == ComputeStorageTypeEnum.nas:
                request.setString(ParamKeyDefine.image, image.path)
                self.info("[%08X] <create_host> create from image '%s'('%s'), nas path '%s'"%
                          (session.session_id, image.name, image.uuid, image.path))
            else:
                self.info("[%08X] <create_host> create from image '%s'('%s'), container '%s'"%
                          (session.session_id, image.name, image.uuid, image.container))
        
        require = HostRequirement()
        require.cpu_count = request.getUInt(ParamKeyDefine.cpu_count)
        require.memory    = request.getUInt(ParamKeyDefine.memory)
        disk_volume       = request.getUIntArray(ParamKeyDefine.disk_volume)
        for volume in disk_volume:
            require.disk_volume += volume
            if enable_local_backup==EnableLocalBackupEnum.enabled:
                require.backup_disk_volume += volume

        ##key = server uuid, value = service name(node_name)
        service_map = {}
        for resource in compute_pool.resource.values():
            if resource.status == ResourceStatusEnum.enable:
                ##only select enable resource
                service_map[resource.server] = resource.name
            else:
                self.warn("[%08X] <create_host> ignore resource node '%s', resource disabled"%
                          (session.session_id, resource.name))
        
        creating_host_map = {} #format : {node_client_name : [host_info0, host_info1, ...]}
        hosts_in_creating = self.config_manager.getAllCreatingHost()
        for host in hosts_in_creating:
            node_client_name = host.container
            if creating_host_map.has_key(node_client_name):
                creating_host_map[node_client_name].append(host)
            else:
                creating_host_map[node_client_name] = [host] #each nc's creating host
                
        status_host_list = []
        for server_id, node_client_name in service_map.items():#can been used resource(nc) in pool
            if self.status_manager.containsServerStatus(server_id):
                server_status = self.status_manager.getServerStatus(server_id)#nc's status
                hosts         = self.config_manager.queryHosts(node_client_name)#nc's created host
                # add creating hosts into list
                if creating_host_map.has_key(node_client_name):
                    hosts.extend(creating_host_map[node_client_name])
                status_host_list.append( (server_status, hosts))
            else:
                self.warn("[%08X] <create_host> ignore resource server '%s', server status not available"%
                          (session.session_id, server_id))

        server_id = DefaultComputeSelector.selectComputeNode(require, status_host_list)
        if server_id is None:
            self.error("[%08X] <create_host> create host fail, can't select available compute node in pool '%s', resource count %d, require:%d cpu, %d MB mem, %d GB disk"%
                       (session.session_id, compute_pool.name, len(status_host_list), require.cpu_count, require.memory/1048576, require.disk_volume/1073741824))
            self.taskFail(session)
            return   
             
        # target_node is node name of node client
        target_node = service_map[server_id]                                                
        self.info("[%08X] <create_host> select target node '%s' in %d resource(s), require:%d cpu, %d MB mem, %d GB disk"%
                  (session.session_id, target_node, len(status_host_list), require.cpu_count,require.memory/1048576, require.disk_volume/1073741824))
        
        server_status = self.status_manager.getServerStatus(server_id)
        server_ip = server_status.ip
        port = request.getUIntArray(ParamKeyDefine.port)
                
        ##forwarder&allocate address        
        if ComputeNetworkTypeEnum.monopoly == compute_pool.network_type:
            ##mono
            ##check ir
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            
            if default_ir is None:
                self.error("[%08X] <create_host> create host fail, no intelligent router actived for mono host"%
                           (session.session_id))
                self.taskFail(session)
                return
            
            address_pool_id = compute_pool.network
            
            ##allocate public ip
            public_ip = self.address_manager.allocate(address_pool_id)
            if public_ip is None:
                self.error("[%08X] <create_host> create host fail, can't allocate public ip in address pool '%s'"%
                           (session.session_id, address_pool_id))
                self.taskFail(session)
                return
            
            ##forwarder
            forwarder = HostForwarder()
            forwarder.type           = ForwarderTypeEnum.mono
            forwarder.host_name      = host_name
            forwarder.public_ip      = [public_ip]
            forwarder.server_ip      = server_ip
            forwarder.public_monitor = 5900
            forwarder.enable         = False
            
            if not self.forwarder_manager.create(forwarder):
                self.error("[%08X] <create_host> create host fail, can't create mono forwarder"%
                           (session.session_id))
                self.address_manager.deallocate(address_pool_id, public_ip)
                self.taskFail(session)
                return
            
            self.info("[%08X] <create_host> allocate mono forwarder '%s', public display '%s:%d'"%
                      (session.session_id, forwarder.uuid, forwarder.public_ip, forwarder.public_monitor))
            request.setString(ParamKeyDefine.forward, forwarder.uuid)
            ip = [server_ip, public_ip]
            display_port = forwarder.public_monitor
            forwarder_id = forwarder.uuid
            if 0 != len(port):
                new_port = []
                for offset in range(0, len(port), 2):
                    proto = port[offset]
                    host_port = port[offset + 1]
                    ##public port = host port
                    new_port.extend([proto, host_port, host_port])
                port = new_port
                
        elif ComputeNetworkTypeEnum.share == compute_pool.network_type:
            ##share
            ##check ir
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            
            if default_ir is None:
                self.error("[%08X] <create_host> create host fail, no intelligent router actived for share host"%
                           (session.session_id))
                self.taskFail(session)
                return
            
            port_pool_id = compute_pool.network
            port_count   = len(port)
            request_port = math.ceil(float(port_count)/2) + 1
            
            ##allocate public ip & port list
            public_ip, port_list = self.port_manager.allocate(port_pool_id, request_port)
            if public_ip is None:
                self.error("[%08X] <create_host> create host fail, can't allocate public port in port pool '%s'"%
                           (session.session_id, port_pool_id))
                self.taskFail(session)
                return
            
            self.info("[%08X] <create_host> allocate public ip '%s', port '%s'"%
                      (session.session_id, public_ip, port_list))
            
            ##forwarder
            forwarder = HostForwarder()
            forwarder.type           = ForwarderTypeEnum.share
            forwarder.host_name      = host_name
            forwarder.public_ip      = [public_ip]
            forwarder.server_ip      = server_ip
            forwarder.public_monitor = port_list[0]
            forwarder.enable         = False
            
            if 0 != port_count:
                port_list_offset = 1
                new_port = []
                for offset in range(0, len(port), 2):
                    proto       = port[offset]
                    host_port   = port[offset + 1]
                    public_port = port_list[port_list_offset]
                    new_port.extend([proto, host_port, public_port])
                    forward_port             = ForwarderPort()
                    forward_port.public_port = public_port
                    forward_port.host_port   = host_port
                    forwarder.port.append(forward_port)
                    port_list_offset += 1
                port = new_port
                
            if not self.forwarder_manager.create(forwarder):
                self.error("[%08X] <create_host> create host fail, can't create share forwarder" %
                           (session.session_id))
                self.port_manager.deallocate(port_pool_id, public_ip, port_list)
                self.taskFail(session)
                return
            
            self.info("[%08X] <create_host> allocate share forwarder '%s', public display '%s:%d', %d port(s) allocated" %
                      (session.session_id, forwarder.uuid, forwarder.public_ip, forwarder.public_monitor, len(port_list)))
            
            request.setString(ParamKeyDefine.forward, forwarder.uuid)
            ip = [server_ip, public_ip]
            display_port = forwarder.public_monitor
            forwarder_id = forwarder.uuid
            
        else:
            ##private
            ##no public ip allocated
            ip = [server_ip, ""]
            display_port = 0
            forwarder_id = ""
            if 0 != len(port):
                new_port = []
                for offset in range(0, len(port), 2):
                    proto = port[offset]
                    host_port = port[offset + 1]
                    new_port.extend([proto, host_port, 0])
                port = new_port

        request.setStringArray(ParamKeyDefine.ip,        ip)
        request.setUInt(ParamKeyDefine.display_port,     display_port)
        request.setUIntArray(ParamKeyDefine.port,        port)
        request.setString(ParamKeyDefine.forward,        forwarder_id)
        request.setUInt(ParamKeyDefine.network_type,     compute_pool.network_type)
        request.setString(ParamKeyDefine.network_source, compute_pool.network)
        request.setUInt(ParamKeyDefine.disk_type,        compute_pool.disk_type)
        request.setString(ParamKeyDefine.disk_source,    compute_pool.disk_source)
        request.setUIntArray(ParamKeyDefine.option,      [use_image, data_disk_count, auto_start, enable_local_backup, enable_usb_extention, compute_pool.thin_provisioning, compute_pool.backing_image, video_type])

        session.target  = target_node
        request.session = session.session_id
        
        
        #add host info in creating map
        host_info = HostInfo()
        host_info.container           = target_node
        host_info.cpu_count           = _parameter["cpu_count"]
        host_info.memory              = _parameter["memory"]
        host_info.disk_volume         = _parameter["disk_volume"]
        host_info.enable_local_backup = enable_local_backup
        host_info.thin_provisioning   = compute_pool.thin_provisioning
        host_info.backing_image       = compute_pool.backing_image
        host_info.video_type          = video_type
        
        session._ext_data["createing_host"] = host_info
        
        self.config_manager.addCreatingHost(session.session_id, host_info)
            
        # send to node client
        self.sendMessage(request, target_node)
        self.setLoopTimer(session, self.notify_interval)
        self.info("[%08X] <create_host> request create host '%s' to compute node '%s'..."%
                  (session.session_id, host_name, target_node))
    
    
    def onCreateSuccess(self, response, session):
        self.clearTimer(session)
        request = session.initial_message
        
        #remove host info in creating map
        self.config_manager.removeCreatingHost(session.session_id)
        
        host = session._ext_data["createing_host"]
        
        # host = HostInfo()
        host.uuid = response.getString(ParamKeyDefine.uuid)
        host.pool = request.getString(ParamKeyDefine.pool)
        
        if self.config_manager.containsHost(host.uuid):
            self.error("[%08X] <create_host> create host success, but host id '%s' already exists"%
                       (session.session_id, host.uuid))
            self.clearResource(session)
            self.taskFail(session)
            return
        
        host.container       = session.target
        host.name            = request.getString(ParamKeyDefine.name)
        host.cpu_count       = request.getUInt(ParamKeyDefine.cpu_count)
        host.memory          = request.getUInt(ParamKeyDefine.memory)
        
        option                   = request.getUIntArray(ParamKeyDefine.option)
        host.data_disk_count     = option[1]
        host.auto_start          = (1 == option[2])
        
        if len(option)>=4:
            host.enable_local_backup = option[3]
            
        if len(option)>=5:
            host.enable_usb_ext      = option[4]
        
        host.disk_volume     = request.getUIntArray(ParamKeyDefine.disk_volume)

        host.user               = request.getString(ParamKeyDefine.user)
        host.group              = request.getString(ParamKeyDefine.group)
        host.display            = request.getString(ParamKeyDefine.display)
        host.authentication     = request.getString(ParamKeyDefine.authentication)
        host.network            = request.getString(ParamKeyDefine.network)
        host.inbound_bandwidth  = request.getUInt(ParamKeyDefine.inbound_bandwidth)
        host.outbound_bandwidth = request.getUInt(ParamKeyDefine.outbound_bandwidth)
        host.max_iops           = request.getUInt(ParamKeyDefine.io)
        host.cpu_priority       = request.getUInt(ParamKeyDefine.priority)
        host.forwarder          = request.getString(ParamKeyDefine.forward)
        host.network_type       = request.getUInt(ParamKeyDefine.network_type)
        host.network_source     = request.getString(ParamKeyDefine.network_source)
        host.disk_type          = request.getUInt(ParamKeyDefine.disk_type)
        host.disk_source        = request.getString(ParamKeyDefine.disk_source)
        
        ##add to config
        ip = response.getStringArray(ParamKeyDefine.ip)
        host.server_ip = ip[0]
        host.public_ip = ip[1]
        
        display_port = response.getUIntArray(ParamKeyDefine.display_port)
        host.server_port = display_port[0]
        host.public_port = display_port[1]
        
        host.output_port_range = response.getUIntArray(ParamKeyDefine.range)
        
        ##nat port
        nat_list = response.getUIntArray(ParamKeyDefine.nat)
        if 0 != (len(nat_list)%4):
            self.error("[%08X] <create_host> create host success, but nat port list is invalid(length %d)"%
                       (session.session_id, len(nat_list)))
            self.clearResource(session)
            self.taskFail(session)
            return
        
        for offset in range(0, len(nat_list), 4):
            port = HostPort()
            port.protocol    = nat_list[offset]
            port.server_port = nat_list[offset + 1]
            port.host_port   = nat_list[offset + 2]
            port.public_port = nat_list[offset + 3]
            host.port.append(port)

        if not self.config_manager.addHost(host):
            self.error("[%08X] <create_host> create host success, but add host '%s' fail"%
                       (session.session_id, host.name))
            self.clearResource(session)
            self.taskFail(session)
            return
        
        self.info("[%08X] <create_host> create host success, host '%s'('%s')"%
                  (session.session_id, host.name, host.uuid))
        total_disk = 0
        for volume in host.disk_volume:
            total_disk += volume

        self.info("[%08X] <create_host> cpu %d, memory %d MB, total disk %d GB"%
                  (session.session_id, host.cpu_count, host.memory/1048576, total_disk/1073741824))
        self.info("[%08X] <create_host> monitor address '%s:%d', %d port opened"%
                  (session.session_id, host.server_ip, host.server_port, len(host.port)))
        
        ##add to resource
        if self.compute_pool_manager.containsResource(host.pool, session.target):
            resource = self.compute_pool_manager.getResource(host.pool, session.target)
            resource.addHost(host.uuid)
            self.info("[%08X] <create_host> add host '%s' to compute resource '%s'"%
                      (session.session_id, host.name, resource.name))
            ##save
            self.compute_pool_manager.savePoolResource(host.pool, resource.name)

        ##save host uuid to session target
        session.target = host.uuid

        if ComputeNetworkTypeEnum.monopoly == host.network_type:
            ##update forwarder
            ##check ir
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            if default_ir is None:
                self.error("[%08X] <create_host> create host fail, no intelligent router actived for mono host"%
                           (session.session_id))
                self.clearResource(session)
                self.taskFail(session)
                return
            
            forwarder_id = host.forwarder
            
            forwarder = HostForwarder()
            forwarder.host_id        = host.uuid
            forwarder.server_ip      = host.server_ip
            forwarder.server_monitor = host.server_port
            
            self.forwarder_manager.modify(forwarder_id, forwarder)
            self.info("[%08X] <create_host> update mono forwarder '%s', host id '%s', server monitor port '%s:%d'"%
                      (session.session_id, forwarder_id, forwarder.host_id, forwarder.server_ip, forwarder.server_monitor))
            ##send request
            forwarder = self.forwarder_manager.get(forwarder_id)
            
            add_request = getRequest(RequestDefine.add_forwarder)
            add_request.session = session.session_id
            add_request.setString(ParamKeyDefine.uuid, forwarder.uuid)
            add_request.setUInt(ParamKeyDefine.type,   forwarder.type)
            add_request.setString(ParamKeyDefine.host, forwarder.host_id)
            add_request.setString(ParamKeyDefine.name, forwarder.host_name)
            add_request.setUInt(ParamKeyDefine.status, 1 if (forwarder.enable==True) else 0)
            
            ip = [forwarder.server_ip]
            ip.extend(forwarder.public_ip)
            add_request.setStringArray(ParamKeyDefine.ip, ip)
            add_request.setUIntArray(ParamKeyDefine.display_port, [forwarder.server_monitor, forwarder.public_monitor])
            add_request.setUIntArray(ParamKeyDefine.port, [])
            
            self.sendMessage(add_request, default_ir)
            self.setTimer(session, self.operate_timeout)
            
            self.info("[%08X] <create_host> request add forwarder '%s' to intelligent router '%s'..."%
                      (session.session_id, forwarder.uuid, default_ir))
            return
        
        elif ComputeNetworkTypeEnum.share == host.network_type:
            ##update forwarder
            ##check ir
            default_ir = self.message_handler.getDefaultIntelligentRouter()
            if default_ir is None:
                self.error("[%08X] <create_host> create host fail, no intelligent router actived for share host"%
                           (session.session_id))
                self.clearResource(session)
                self.taskFail(session)
                return
            
            forwarder_id = host.forwarder
            
            # forwarder = HostForwarder()
            forwarder = self.forwarder_manager.get(forwarder_id)
            if forwarder==None:
                forwarder = HostForwarder()
            
            forwarder.host_id           = host.uuid
            forwarder.server_monitor    = host.server_port
            forwarder.output_port_range = host.output_port_range
            
            forwarder.port = []
            port_list = []
            if 0 != len(host.port):
                for allocated_port in host.port:
                    forward_port = ForwarderPort()
                    forward_port.server_port = allocated_port.server_port
                    forward_port.host_port   = allocated_port.host_port
                    forward_port.public_port = allocated_port.public_port
                    port_list.extend([allocated_port.server_port,
                                      allocated_port.public_port,
                                      allocated_port.host_port])
                    forwarder.port.append(forward_port)
                    
            forwarder.computeSignature()
            self.forwarder_manager.put(forwarder)
            self.info("[%08X] <create_host> update share forwarder '%s', host id '%s', server monitor port %d, %d port(s)"%
                      (session.session_id, forwarder_id, forwarder.host_id, forwarder.server_monitor, len(port_list)))
            
            ##send request
            #forwarder = self.forwarder_manager.get(forwarder_id)
            
            add_request = getRequest(RequestDefine.add_forwarder)
            
            add_request.session = session.session_id
            add_request.setString(ParamKeyDefine.uuid,     forwarder.uuid)
            add_request.setUInt(ParamKeyDefine.type,       forwarder.type)
            add_request.setString(ParamKeyDefine.host,     forwarder.host_id)
            add_request.setString(ParamKeyDefine.name,     forwarder.host_name)
            add_request.setUInt(ParamKeyDefine.status,     1 if (forwarder.enable==True) else 0)
            add_request.setUIntArray(ParamKeyDefine.range, forwarder.output_port_range)
            
            ip = [forwarder.server_ip]
            ip.extend(forwarder.public_ip)
            
            add_request.setStringArray(ParamKeyDefine.ip, ip)
            add_request.setUIntArray(ParamKeyDefine.display_port, [forwarder.server_monitor, forwarder.public_monitor])
            add_request.setUIntArray(ParamKeyDefine.port, port_list)
            
            self.sendMessage(add_request, default_ir)
            self.setTimer(session, self.operate_timeout)
            
            self.info("[%08X] <create_host> request add forwarder '%s' to intelligent router '%s'..."%
                      (session.session_id, forwarder.uuid, default_ir))
            
            return          
          
        else:
            ##private
            self.forwarder_manager.enable(host.forwarder)
            response.session = session.request_session
            self.sendMessage(response, session.request_module)
            session.finish()

    def onCreateStarted(self, event, session):
        self.info("[%08X] <create_host> create host started"%
                  session.session_id)
        event.session = session.request_session
        self.sendMessage(event, session.request_module)

    def onCreateReport(self, event, session):
        session.counter = 0
        progress = event.getUInt(ParamKeyDefine.level)
        self.info("[%08X] <create_host> create host on progress %d%%..."%
                  (session.session_id, progress))
        ##store progress
        session.offset = progress
        
    def onCreateFail(self, response, session):
        self.clearTimer(session)
        self.error("[%08X] <create_host> create host fail"%
                   session.session_id)
        self.clearResource(session)
        self.taskFail(session)
        
    def onCreateTimeout(self, response, session):
        session.counter += 1
        if session.counter >= self.max_timeout:
            self.error("[%08X] <create_host> create host exceed max timeout( %d/ %d)"%
                       (session.session_id, session.counter, self.max_timeout))
            self.clearResource(session)
            self.taskFail(session)
            return
        ##notify progress
        event = getEvent(EventDefine.report)
        event.success = True
        event.session = session.request_session
        event.setUInt(ParamKeyDefine.level, session.offset)        
        self.sendMessage(event, session.request_module)
            
    def clearResource(self, session):
        request = session.initial_message
        forwarder_id = request.getString(ParamKeyDefine.forward)
        if 0 != len(forwarder_id):
            if not self.forwarder_manager.contains(forwarder_id):
                return
            forwarder = self.forwarder_manager.get(forwarder_id)
            pool_id = request.getString(ParamKeyDefine.network_source)
            public_ip = forwarder.public_ip[0]
            if ForwarderTypeEnum.mono == forwarder.type:                
                self.address_manager.deallocate(pool_id, public_ip)
            elif ForwarderTypeEnum.share == forwarder.type:
                port_list = [forwarder.public_monitor]
                if 0 != len(forwarder.port):
                    for forward_port in forwarder.port:
                        port_list.append(forward_port.public_port)
                self.port_manager.deallocate(pool_id, public_ip, port_list)
            if 0 != len(forwarder.host_id):
                if self.config_manager.containsHost(forwarder.host_id):
                    host = self.config_manager.getHost(forwarder.host_id)
                    if 0 != len(host.pool):
                        resource = self.compute_pool_manager.getResource(host.pool, host.container)
                        resource.removeHost(host.uuid)
                        ##save
                        self.compute_pool_manager.savePoolResource(host.pool, resource.name)
                    if 0 != len(host.container):
                        delete_msg = getRequest(RequestDefine.delete_host)
                        delete_msg.session = session.session_id
                        delete_msg.setString(ParamKeyDefine.uuid, host.uuid)
                        self.sendMessage(delete_msg, host.container)
                    self.config_manager.removeHost(forwarder.host_id)
            self.forwarder_manager.delete(forwarder_id)
            
        #remove host info in creating map
        self.config_manager.removeCreatingHost(session.session_id)

    #---------------------
    
    def onAddSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <create_host> add forwarder success"%
                  session.session_id)
        
        response = getResponse(RequestDefine.create_host)
        response.success = True
        response.session = session.request_session

        host = self.config_manager.getHost(session.target)
        forwarder_id = host.forwarder
        ##enable for mono&share host
        self.forwarder_manager.enable(forwarder_id)
        
        response.setString(ParamKeyDefine.uuid, host.uuid)
        response.setStringArray(ParamKeyDefine.ip, [host.server_ip, host.public_ip])
        response.setUIntArray(ParamKeyDefine.display_port, [host.server_port, host.public_port])
        nat_port = []
        for port in host.port:
            nat_port.extend([port.protocol, port.server_port, port.host_port, port.public_port])
            
        self.sendMessage(response, session.request_module)
        session.finish()
        
    def onAddFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <create_host> add forwarder fail"%
                   session.session_id)
        self.clearResource(session)
        self.taskFail(session)
        
    def onAddTimeout(self, msg, session):
        self.error("[%08X] <create_host> add forwarder timeout"%
                   session.session_id)
        self.clearResource(session)
        self.taskFail(session)        

    #---------------------
    

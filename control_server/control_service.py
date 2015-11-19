#!/usr/bin/python
import os
import os.path
import datetime
from service.message_define import *
from service.node_service import *
from config_manager import *
from status_manager import *
from monitor_manager import *

from data.monitor_level import *
from task.control_trans_manager import *
from task.task_type import *

from status_enum import *
from host_status import *
from server_status import *
from server_rack_status import *
from server_room_status import *
from system_status import *
from service_manager import *

from compute_pool_status import *

from address_manager import *
from port_manager import *
from storage_pool_manager import *
from compute_pool_manager import *
from forwarder_manager import *

from iso_manager import *
from image_manager import *
from expire_manager import *
import threading
from network_manager import NetworkManager
from snapshot_pool_manager import SnapshotPoolManager
import fcntl

class ControlService(NodeService):
    """
    base:NodeService
    
    usage:
    attrib:
        server_rack
        server
        server_name
        domain
        group
        node
        type
        version
        local_ip
        local_port
        domain_server

    methods:
    
    bind(ip):
    start():
    stop():
    sendMessage(msg, receiver):
    sendMessageToSelf(msg):
    connectRemoteNode(remote_ip, remote_port):
    
    setTimer(timeout, receive_session):
        invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        
    setLoopTimer(timeout, receive_session):
        continues invoke timeout event to [receive_session] after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        
    setTimedEvent(event, timeout):
        invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        
    setLoopTimedEvent(event, timeout):
        continues invoke specified [event] to handler after [timeout] seconds
        @return:timer_id
        stop by clearTimer()
        
    clearTimer(timer_id):
        cancel timeout count down
    

    methods need override by subclass:
    onStart():
        onStart:subclass must call NodeService.onStart() first
        @return:
        False = initial fail, stop service
        True = initial success, start main service
        
    onStop():
        onStop:subclass must call NodeService.onStop() first

    onChannelConnected(node_name, node_type):
    onChannelDisconnected(node_name, node_type):
    handleEventMessage(event, sender):
    handleRequestMessage(request, sender):
    handleResponseMessage(response, sender):
    """
    
    version = "2.1#20151110-1"

    config_root = "/var/zhicloud/config/control_server"
    base_log_dir = "/var/zhicloud/log"
    version_log = "version_track.log"

    monitor_timer_session = 1
    monitor_timer_id = 0
    monitor_data_interval = 2

    status_timer_session = 2
    status_timer_id = 0
    status_timer_interval = 5

    statistic_timer_session = 3
    statistic_timer_id = 0
    statistic_timer_interval = 60

    synchronize_timer_session = 4
    synchronize_timer_id = 0
    synchronize_timer_interval = 1

    storage_server_sync_session = 5
    storage_server_sync_timer_id = 0
    storage_server_sync_timer_interval = 10

    statistic_server = ""
    statistic_timeout = 0
    max_statistic_timeout = 5
    task_thread = 5

    def __init__(self,
                 service_name, domain, ip, group_ip, group_port,
                 server, rack, server_name, proxy):
        NodeService.__init__(self, NodeTypeDefine.control_server,
                             service_name, domain, ip,
                             (5600 + NodeTypeDefine.control_server), 200,
                             group_ip, group_port, ControlService.version,
                             server, rack, server_name, proxy)
        self.version_log_path = os.path.join(self.base_log_dir, self.version_log);
        self._log_start()

        resource_path = os.path.join(self.config_root, "resource")

        if not os.path.exists(resource_path):
            os.mkdir(resource_path)

        # #key = node name,value = session_id
        self.sync_session = {}
        self.observe_session = {}

        self.storage_server = []
        self.storage_server_lock = threading.RLock()
        
        self.intelligent_router = []
        self.intelligent_router_lock = threading.RLock()

        self._data_indexes = []
        self._data_indexes_lock = threading.RLock()

        self.status_manager = StatusManager(self.name)
        self.config_manager = ConfigManager(self.name)
        self.monitor_manager = MonitorManager(self.name)
        self.service_manager = ServiceManager("%s.service" % self.name)
        self.address_manager = AddressManager(resource_path, "%s.address" % self.name)

        self.port_manager = PortManager(resource_path, "%s.address" % self.name)

        self.storage_pool_manager = StoragePoolManager()
        self.compute_pool_manager = ComputePoolManager(resource_path, "%s.compute_resource" % self.name)
        self.snapshot_pool_manager = SnapshotPoolManager()
        self.network_manager = NetworkManager(resource_path, "%s.network_manager" % self.name)
        self.forwarder_manager = ForwarderManager(resource_path, "%s.forwarder" % self.name)

        self.iso_manager = ISOManager("%s.iso" % self.name)
        self.image_manager = ImageManager("%s.image" % self.name)
        self.expire_manager = ExpireManager()

        self.control_trans_manager = ControlTransManager(
            self.name, self,
            self.status_manager,
            self.config_manager,
            self.iso_manager,
            self.compute_pool_manager,
            self.storage_pool_manager,
            self.address_manager,
            self.port_manager,
            self.service_manager,
            self.image_manager,
            self.forwarder_manager,
            self.expire_manager,
            self.network_manager,
            self.snapshot_pool_manager,
            self.task_thread)

    def _log_start(self):
        with io.open(self.version_log_path, "ab") as _file:
            fcntl.flock(_file, fcntl.LOCK_EX)
            _file.write("%s: service %s (version %s) start\r\n" % (datetime.datetime.now(), self.node, self.version))

    def _log_stop(self):
        with io.open(self.version_log_path, "ab") as _file:
            fcntl.flock(_file, fcntl.LOCK_EX)
            _file.write("%s: service %s (version %s) stop\r\n" % (datetime.datetime.now(), self.node, self.version))

    def initialize(self):
        self.compute_pool_manager.load()
        self.network_manager.load()
        self.forwarder_manager.load()
        self.address_manager.load()
        self.port_manager.load()
        self.console("<control_service> %s initilized" % self.name)
        self.info("<control_service> %s initilized" % self.name)
        return True;

    def onStart(self):
        """
        onStart:subclass must call NodeService.onStart() first
        @return:
        False = initial fail, stop service
        True = initial success, start main service
        """
        if not self.initialize():
            return False
        if not NodeService.onStart(self):
            return False
        self.monitor_timer_id = self.setLoopTimer(self.monitor_data_interval,
                                                  self.monitor_timer_session)
        self.status_timer_id = self.setLoopTimer(self.status_timer_interval,
                                                 self.status_timer_session)
        self.synchronize_timer_id = self.setLoopTimer(self.synchronize_timer_interval,
                                                      self.synchronize_timer_session)

        self.storage_server_sync_timer_id = self.setLoopTimer(self.storage_server_sync_timer_interval,
                                                              self.storage_server_sync_session)
        self.control_trans_manager.start()
        return True

    def onStop(self):
        """
        onStop:subclass must call NodeService.onStop() first
        """
        self._log_stop()
        self.clearTimer(self.monitor_timer_id)
        self.clearTimer(self.status_timer_id)
        self.clearTimer(self.synchronize_timer_id)
        self.clearTimer(self.storage_server_sync_timer_id)
        if 0 != self.statistic_timer_id:
            self.clearTimer(self.statistic_timer_id)

        self.control_trans_manager.stop()
        NodeService.onStop(self)
        self.synchronizeData()

    def onChannelConnected(self, node_name, node_type, remote_ip, remote_port):
        self.info("<control_service> channel connected, node name '%s', type: %d" % (node_name, node_type))
        if NodeTypeDefine.node_client == node_type:
            return self.onClientConnected(node_name)
        elif NodeTypeDefine.data_server == node_type:
            return self.onDataServerConnected(node_name)
        elif NodeTypeDefine.storage_server == node_type:
            return self.onStorageConnected(node_name)
        elif NodeTypeDefine.intelligent_router == node_type:
            return self.onIntelligentRouterConnected(node_name)
        elif NodeTypeDefine.data_index == node_type:
            return self.onDataIndexConnected(node_name)

    def onStorageConnected(self, storage_server):
        self.info("<control_service> storage server ready, name '%s'" % storage_server)
        with self.storage_server_lock:
            if storage_server not in self.storage_server:
                self.storage_server.append(storage_server)

        ## initial storage : query iso image and disk image
        session_id = self.control_trans_manager.allocTransaction(initial_storage)
        request = getRequest(RequestDefine.invalid)
        setString(request, ParamKeyDefine.target, storage_server)
        self.control_trans_manager.startTransaction(session_id, request)
        
        ## storage server sync : query whisper
        session_id = self.control_trans_manager.allocTransaction(storage_server_sync)
        request = getRequest(RequestDefine.invalid)
        request.setString(ParamKeyDefine.target, storage_server)
        self.control_trans_manager.startTransaction(session_id, request)

        # # synch storage_server status
        session_id = self.control_trans_manager.allocTransaction(synch_service_status)
        request = getRequest(RequestDefine.invalid)
        request.setString(ParamKeyDefine.target, storage_server)
        self.control_trans_manager.startTransaction(session_id, request)

    def onChannelDisconnected(self, node_name, node_type):
        self.info("<control_service> channel disconnected, node name '%s', type: %d" % (node_name, node_type))
        if NodeTypeDefine.node_client == node_type:
            return self.onClientDisconnected(node_name)
        elif NodeTypeDefine.statistic_server == node_type:
            return self.onStatisticServerDisconnected(node_name)
        elif NodeTypeDefine.intelligent_router == node_type:
            return self.onIntelligentRouterDisconnected(node_name)
        elif NodeTypeDefine.storage_server == node_type:
            return self.onStorageServerDisconnected(node_name)

    def onStorageServerDisconnected(self, node_name):
        with self.storage_server_lock:
            if node_name in self.storage_server:
                self.storage_server.remove(node_name)
                
        self.image_manager.removeAllImageInContainer(node_name)
        self.iso_manager.removeAllImageInContainer(node_name)

    def onIntelligentRouterConnected(self, node_name):
        with self.intelligent_router_lock:
            if node_name not in self.intelligent_router:
                self.intelligent_router.append(node_name)

    def onDataIndexConnected(self, node_name):
        #
        with self._data_indexes_lock:
            if node_name not in self._data_indexes:
                self._data_indexes.append(node_name)

        # initialize storage pool
        session_id = self.control_trans_manager.allocTransaction(initial_storage_pool)
        request = getRequest(RequestDefine.invalid)
        request.setString(ParamKeyDefine.target, node_name)
        self.control_trans_manager.startTransaction(session_id, request)

        # initialize snapshot pool
        session_id = self.control_trans_manager.allocTransaction(initial_snapshot_pool)
        request = getRequest(RequestDefine.invalid)
        request.setString(ParamKeyDefine.target, node_name)
        self.control_trans_manager.startTransaction(session_id, request)

    def getDefaultDataIndex(self):
        with self._data_indexes_lock:
            try:
                return self._data_indexes[0]
            except:
                return None


    def sendToDefaultDataIndex(self, msg):
        # get target data_index
        _data_index = self.getDefaultDataIndex()
        # send to target data_index
        if _data_index == None:
            self.error("<control_service> send message to data_index fail, no data index available.")
            return False
        else:
            self.sendMessage(msg, _data_index)
            return True


    def onIntelligentRouterDisconnected(self, node_name):
        with self.intelligent_router_lock:
            if node_name in self.intelligent_router:
                self.intelligent_router.remove(node_name)

    def getDefaultIntelligentRouter(self):
        with self.intelligent_router_lock:
            if 0 == len(self.intelligent_router):
                return None
            else:
                return self.intelligent_router[0]

    def handleEventMessage(self, event, sender):
        try:
            if 0 != event.session:
                if self.control_trans_manager.containsTransaction(event.session):
                    return self.control_trans_manager.processMessage(event.session, event)

            if event.id == EventDefine.service_status_changed:
                return self.handleServiceStatusChanged(event, sender)

            elif event.id == EventDefine.timeout:
                return self.handleTimeout(event, sender)

            elif event.id == EventDefine.monitor_heart_beat:
                return self.handleMonitorHeartBeat(event, sender)

            elif event.id == EventDefine.keep_alive:
                return self.handleKeepAlive(event, sender)

            self.info("<control_service> ignore event id %d from '%s'" % (event.id, sender))

        except Exception as e:
            self.console("<control_service> handle event exception, event %d[%08X], sender '%s', messasge:%s" %
                         (event.id, event.session, sender, e.args))
            self.exception("<control_service> handle event exception, event %d[%08X], sender '%s', messasge:%s" %
                         (event.id, event.session, sender, e.args))


    def handleRequestMessage(self, request, sender):
        try:
            if request.id == RequestDefine.start_monitor:
                return self.handleStartMonitorRequest(request, sender)
            elif request.id == RequestDefine.stop_monitor:
                return self.handleStopMonitorRequest(request, sender)
            elif request.id == RequestDefine.start_statistic:
                return self.handleStartStatisticRequest(request, sender)
            elif request.id == RequestDefine.stop_statistic:
                return self.handleStopStatisticRequest(request, sender)
            elif request.id == EventDefine.config_changed:
                self.warn("<control_service> receive config changed request but ignore")
                return True

            # #initial request
            session_id = None
            if request.id == RequestDefine.query_server_room:
                session_id = self.control_trans_manager.allocTransaction(query_server_room)
            elif request.id == RequestDefine.create_server_room:
                session_id = self.control_trans_manager.allocTransaction(create_server_room)
            elif request.id == RequestDefine.delete_server_room:
                session_id = self.control_trans_manager.allocTransaction(delete_server_room)
            elif request.id == RequestDefine.modify_server_room:
                session_id = self.control_trans_manager.allocTransaction(modify_server_room)

            elif request.id == RequestDefine.query_server_rack:
                session_id = self.control_trans_manager.allocTransaction(query_server_rack)
            elif request.id == RequestDefine.create_server_rack:
                session_id = self.control_trans_manager.allocTransaction(create_server_rack)
            elif request.id == RequestDefine.delete_server_rack:
                session_id = self.control_trans_manager.allocTransaction(delete_server_rack)
            elif request.id == RequestDefine.modify_server_rack:
                session_id = self.control_trans_manager.allocTransaction(modify_server_rack)

            elif request.id == RequestDefine.query_server:
                session_id = self.control_trans_manager.allocTransaction(query_server)
            elif request.id == RequestDefine.add_server:
                session_id = self.control_trans_manager.allocTransaction(add_server)
            elif request.id == RequestDefine.remove_server:
                session_id = self.control_trans_manager.allocTransaction(remove_server)
            elif request.id == RequestDefine.modify_server:
                session_id = self.control_trans_manager.allocTransaction(modify_server)

            elif request.id == RequestDefine.query_service_type:
                session_id = self.control_trans_manager.allocTransaction(query_service_type)
            elif request.id == RequestDefine.query_service_group:
                session_id = self.control_trans_manager.allocTransaction(query_service_group)
            elif request.id == RequestDefine.query_service:
                session_id = self.control_trans_manager.allocTransaction(query_service)
            elif request.id == RequestDefine.modify_service:
                session_id = self.control_trans_manager.allocTransaction(modify_service)
            elif request.id == RequestDefine.query_whisper:
                session_id = self.control_trans_manager.allocTransaction(query_whisper)

            elif request.id == RequestDefine.query_operate_detail:
                if 0 == len(self.statistic_server):
                    self.warn("receive query operate detail request from '%s', but no statistic server available" % (sender))
                    return
                setString(request, ParamKeyDefine.server, self.statistic_server)
                session_id = self.control_trans_manager.allocTransaction(query_operate_detail)
            elif request.id == RequestDefine.query_operate_summary:
                if 0 == len(self.statistic_server):
                    self.warn("receive query operate summary request from '%s', but no statistic server available" % (sender))
                    return
                setString(request, ParamKeyDefine.server, self.statistic_server)
                session_id = self.control_trans_manager.allocTransaction(query_operate_summary)

            elif request.id == RequestDefine.query_service_detail:
                if 0 == len(self.statistic_server):
                    self.warn("receive query service detail request from '%s', but no statistic server available" % (sender))
                    return
                setString(request, ParamKeyDefine.server, self.statistic_server)
                session_id = self.control_trans_manager.allocTransaction(query_service_detail)
            elif request.id == RequestDefine.query_service_summary:
                if 0 == len(self.statistic_server):
                    self.warn("receive query service summary request from '%s', but no statistic server available" % (sender))
                    return
                setString(request, ParamKeyDefine.server, self.statistic_server)
                session_id = self.control_trans_manager.allocTransaction(query_service_summary)
                """
                new request for 2.0
                """
            elif request.id == RequestDefine.query_address_pool:
                session_id = self.control_trans_manager.allocTransaction(query_address_pool)
            elif request.id == RequestDefine.create_address_pool:
                session_id = self.control_trans_manager.allocTransaction(create_address_pool)
            elif request.id == RequestDefine.delete_address_pool:
                session_id = self.control_trans_manager.allocTransaction(delete_address_pool)
            elif request.id == RequestDefine.add_address_resource:
                session_id = self.control_trans_manager.allocTransaction(add_address_resource)
            elif request.id == RequestDefine.remove_address_resource:
                session_id = self.control_trans_manager.allocTransaction(remove_address_resource)
            elif request.id == RequestDefine.query_address_resource:
                session_id = self.control_trans_manager.allocTransaction(query_address_resource)

            elif request.id == RequestDefine.query_port_pool:
                session_id = self.control_trans_manager.allocTransaction(query_port_pool)
            elif request.id == RequestDefine.create_port_pool:
                session_id = self.control_trans_manager.allocTransaction(create_port_pool)
            elif request.id == RequestDefine.delete_port_pool:
                session_id = self.control_trans_manager.allocTransaction(delete_port_pool)
            elif request.id == RequestDefine.add_port_resource:
                session_id = self.control_trans_manager.allocTransaction(add_port_resource)
            elif request.id == RequestDefine.remove_port_resource:
                session_id = self.control_trans_manager.allocTransaction(remove_port_resource)
            elif request.id == RequestDefine.query_port_resource:
                session_id = self.control_trans_manager.allocTransaction(query_port_resource)

            elif request.id == RequestDefine.query_compute_pool:
                session_id = self.control_trans_manager.allocTransaction(query_compute_pool)
            elif request.id == RequestDefine.query_compute_pool_detail:
                session_id = self.control_trans_manager.allocTransaction(query_compute_pool_detail)
            elif request.id == RequestDefine.create_compute_pool:
                session_id = self.control_trans_manager.allocTransaction(create_compute_pool)
            elif request.id == RequestDefine.delete_compute_pool:
                session_id = self.control_trans_manager.allocTransaction(delete_compute_pool)
            elif request.id == RequestDefine.add_compute_resource:
                session_id = self.control_trans_manager.allocTransaction(add_compute_resource)
            elif request.id == RequestDefine.remove_compute_resource:
                session_id = self.control_trans_manager.allocTransaction(remove_compute_resource)
            elif request.id == RequestDefine.query_compute_resource:
                session_id = self.control_trans_manager.allocTransaction(query_compute_resource)

            elif request.id == RequestDefine.query_storage_pool:
                session_id = self.control_trans_manager.allocTransaction(query_storage_pool)
            elif request.id == RequestDefine.create_storage_pool:
                session_id = self.control_trans_manager.allocTransaction(create_storage_pool)
            elif request.id == RequestDefine.modify_storage_pool:
                session_id = self.control_trans_manager.allocTransaction(modify_storage_pool)
            elif request.id == RequestDefine.delete_storage_pool:
                session_id = self.control_trans_manager.allocTransaction(delete_storage_pool)
            elif request.id == RequestDefine.add_storage_resource:
                session_id = self.control_trans_manager.allocTransaction(add_storage_resource)
            elif request.id == RequestDefine.remove_storage_resource:
                session_id = self.control_trans_manager.allocTransaction(remove_storage_resource)
            elif request.id == RequestDefine.query_storage_resource:
                session_id = self.control_trans_manager.allocTransaction(query_storage_resource)

            elif request.id == RequestDefine.query_host:
                session_id = self.control_trans_manager.allocTransaction(query_host)
            elif request.id == RequestDefine.query_host_info:
                session_id = self.control_trans_manager.allocTransaction(query_host_info)
            elif request.id == RequestDefine.create_host:
                session_id = self.control_trans_manager.allocTransaction(create_host)
            elif request.id == RequestDefine.delete_host:
                session_id = self.control_trans_manager.allocTransaction(delete_host)
            elif request.id == RequestDefine.modify_host:
                session_id = self.control_trans_manager.allocTransaction(modify_host)
            elif request.id == RequestDefine.start_host:
                session_id = self.control_trans_manager.allocTransaction(start_host)
            elif request.id == RequestDefine.stop_host:
                session_id = self.control_trans_manager.allocTransaction(stop_host)
            elif request.id == RequestDefine.halt_host:
                session_id = self.control_trans_manager.allocTransaction(halt_host)
            elif request.id == RequestDefine.reset_host:
                session_id = self.control_trans_manager.allocTransaction(reset_host)
            elif request.id == RequestDefine.insert_media:
                session_id = self.control_trans_manager.allocTransaction(insert_media)
            elif request.id == RequestDefine.change_media:
                session_id = self.control_trans_manager.allocTransaction(change_media)
            elif request.id == RequestDefine.eject_media:
                session_id = self.control_trans_manager.allocTransaction(eject_media)
            elif request.id == RequestDefine.attach_disk:
                session_id = self.control_trans_manager.allocTransaction(attach_disk)
            elif request.id == RequestDefine.detach_disk:
                session_id = self.control_trans_manager.allocTransaction(detach_disk)
            elif request.id == RequestDefine.restart_host:
                session_id = self.control_trans_manager.allocTransaction(restart_host)
            elif request.id == RequestDefine.flush_disk_image:
                session_id = self.control_trans_manager.allocTransaction(flush_disk_image)
            elif request.id == RequestDefine.backup_host:
                session_id = self.control_trans_manager.allocTransaction(backup_host)
            elif request.id == RequestDefine.resume_host:
                session_id = self.control_trans_manager.allocTransaction(resume_backup)
            elif request.id == RequestDefine.query_host_backup:
                session_id = self.control_trans_manager.allocTransaction(query_host_backup)

            elif request.id == RequestDefine.query_iso_image:
                session_id = self.control_trans_manager.allocTransaction(query_iso_image)
            elif request.id == RequestDefine.upload_iso_image:
                session_id = self.control_trans_manager.allocTransaction(upload_iso_image)
            elif request.id == RequestDefine.modify_iso_image:
                session_id = self.control_trans_manager.allocTransaction(modify_iso_image)
            elif request.id == RequestDefine.delete_iso_image:
                session_id = self.control_trans_manager.allocTransaction(delete_iso_image)

            elif request.id == RequestDefine.query_disk_image:
                session_id = self.control_trans_manager.allocTransaction(query_disk_image)
            elif request.id == RequestDefine.modify_disk_image:
                session_id = self.control_trans_manager.allocTransaction(modify_disk_image)
            elif request.id == RequestDefine.delete_disk_image:
                session_id = self.control_trans_manager.allocTransaction(delete_disk_image)
            elif request.id == RequestDefine.create_disk_image:
                session_id = self.control_trans_manager.allocTransaction(create_disk_image)
            elif request.id == RequestDefine.query_application:
                session_id = self.control_trans_manager.allocTransaction(query_application)
            elif request.id == RequestDefine.query_resource_pool:
                session_id = self.control_trans_manager.allocTransaction(query_resource_pool)
            elif request.id == RequestDefine.query_struct:
                session_id = self.control_trans_manager.allocTransaction(query_struct)

            elif request.id == RequestDefine.set_forwarder_status:
                session_id = self.control_trans_manager.allocTransaction(set_forwarder_status)
            elif request.id == RequestDefine.query_forwarder_summary:
                session_id = self.control_trans_manager.allocTransaction(query_forwarder_summary)
            elif request.id == RequestDefine.query_forwarder:
                session_id = self.control_trans_manager.allocTransaction(query_forwarder)
            elif request.id == RequestDefine.get_forwarder:
                session_id = self.control_trans_manager.allocTransaction(get_forwarder)
            elif request.id == RequestDefine.add_forwarder:
                session_id = self.control_trans_manager.allocTransaction(add_forwarder)
            elif request.id == RequestDefine.remove_forwarder:
                session_id = self.control_trans_manager.allocTransaction(remove_forwarder)
            elif request.id == RequestDefine.modify_compute_pool:
                session_id = self.control_trans_manager.allocTransaction(modify_compute_pool)

            # network
            elif request.id == RequestDefine.create_network:
                session_id = self.control_trans_manager.allocTransaction(create_network)

            elif request.id == RequestDefine.modify_network:
                session_id = self.control_trans_manager.allocTransaction(modify_network)

            elif request.id == RequestDefine.delete_network:
                session_id = self.control_trans_manager.allocTransaction(delete_network)

            elif request.id == RequestDefine.query_network:
                session_id = self.control_trans_manager.allocTransaction(query_network)

            elif request.id == RequestDefine.query_network_detail:
                session_id = self.control_trans_manager.allocTransaction(query_network_detail)

            elif request.id == RequestDefine.start_network:
                session_id = self.control_trans_manager.allocTransaction(start_network)

            elif request.id == RequestDefine.stop_network:
                session_id = self.control_trans_manager.allocTransaction(stop_network)

            elif request.id == RequestDefine.query_network_host:
                session_id = self.control_trans_manager.allocTransaction(query_network_host)

            elif request.id == RequestDefine.attach_host:
                session_id = self.control_trans_manager.allocTransaction(attach_host)

            elif request.id == RequestDefine.detach_host:
                session_id = self.control_trans_manager.allocTransaction(detach_host)

            elif request.id == RequestDefine.network_attach_address:
                session_id = self.control_trans_manager.allocTransaction(network_attach_address)

            elif request.id == RequestDefine.network_detach_address:
                session_id = self.control_trans_manager.allocTransaction(network_detach_address)

            elif request.id == RequestDefine.network_bind_port:
                session_id = self.control_trans_manager.allocTransaction(network_bind_port)

            elif request.id == RequestDefine.network_unbind_port:
                session_id = self.control_trans_manager.allocTransaction(network_unbind_port)

            #-----------------
            # about device

            elif request.id == RequestDefine.query_device:
                session_id = self.control_trans_manager.allocTransaction(query_device)

            elif request.id == RequestDefine.create_device:
                session_id = self.control_trans_manager.allocTransaction(create_device)

            elif request.id == RequestDefine.modify_device:
                session_id = self.control_trans_manager.allocTransaction(modify_device)

            elif request.id == RequestDefine.delete_device:
                session_id = self.control_trans_manager.allocTransaction(delete_device)

            #-----------------

            elif request.id == RequestDefine.check_config:
                session_id = self.control_trans_manager.allocTransaction(check_config)

            # snapshot pool
            elif request.id == RequestDefine.query_snapshot_pool:
                session_id = self.control_trans_manager.allocTransaction(query_snapshot_pool)

            elif request.id == RequestDefine.create_snapshot_pool:
                session_id = self.control_trans_manager.allocTransaction(create_snapshot_pool)

            elif request.id == RequestDefine.modify_snapshot_pool:
                session_id = self.control_trans_manager.allocTransaction(modify_snapshot_pool)

            elif request.id == RequestDefine.delete_snapshot_pool:
                session_id = self.control_trans_manager.allocTransaction(delete_snapshot_pool)

            elif request.id == RequestDefine.add_snapshot_node:
                session_id = self.control_trans_manager.allocTransaction(add_snapshot_node)

            elif request.id == RequestDefine.remove_snapshot_node:
                session_id = self.control_trans_manager.allocTransaction(remove_snapshot_node)

            elif request.id == RequestDefine.query_snapshot_node:
                session_id = self.control_trans_manager.allocTransaction(query_snapshot_node)

            # snapshot
            elif request.id == RequestDefine.query_snapshot:
                session_id = self.control_trans_manager.allocTransaction(query_snapshot)

            elif request.id == RequestDefine.create_snapshot:
                session_id = self.control_trans_manager.allocTransaction(create_snapshot)

            elif request.id == RequestDefine.delete_snapshot:
                session_id = self.control_trans_manager.allocTransaction(delete_snapshot)

            elif request.id == RequestDefine.resume_snapshot:
                session_id = self.control_trans_manager.allocTransaction(resume_snapshot)

            elif request.id == RequestDefine.add_rule:
                session_id = self.control_trans_manager.allocTransaction(add_rule)
            elif request.id == RequestDefine.remove_rule:
                session_id = self.control_trans_manager.allocTransaction(remove_rule)
            elif request.id == RequestDefine.query_rule:
                session_id = self.control_trans_manager.allocTransaction(query_rule)

            # storage device
            elif request.id == RequestDefine.query_storage_device:
                session_id = self.control_trans_manager.allocTransaction(query_storage_device)
            elif request.id == RequestDefine.add_storage_device:
                session_id = self.control_trans_manager.allocTransaction(add_storage_device)
            elif request.id == RequestDefine.remove_storage_device:
                session_id = self.control_trans_manager.allocTransaction(remove_storage_device)
            elif request.id == RequestDefine.enable_storage_device:
                session_id = self.control_trans_manager.allocTransaction(enable_storage_device)
            elif request.id == RequestDefine.disable_storage_device:
                session_id = self.control_trans_manager.allocTransaction(disable_storage_device)


            if session_id:
                self.control_trans_manager.startTransaction(session_id, request)
                return
            
            
            self.info("<control_service> ignore request id %d from '%s'" % (request.id, sender))

        except Exception as e:
            self.console("<control_service> handle request exception, request %d[%08X], sender '%s', messasge:%s" %
                         (request.id, request.session, sender, e.args))
            self.error("<control_service> handle request exception, request %d[%08X], sender '%s', messasge:%s" %
                         (request.id, request.session, sender, e.args))

    def handleResponseMessage(self, response, sender):
        try:
            if 0 != response.session:
                if self.control_trans_manager.containsTransaction(response.session):
                    return self.control_trans_manager.processMessage(response.session, response)

            self.info("<control_service> ignore response id %d from '%s'" % (response.id, sender))

        except Exception as e:
            self.console("<control_service> handle response exception, response %d, sender '%s', messasge:%s" % (response.id, sender, e.args))
            self.exception("<control_service> handle response exception, response %d, sender '%s', messasge:%s" % (response.id, sender, e.args))

    def onClientConnected(self, node_name):
        if not self.sync_session.has_key(node_name):
            session_id = self.control_trans_manager.allocTransaction(initial_node)
            self.sync_session[node_name] = session_id
            request = getRequest(RequestDefine.invalid)
            request.setString(ParamKeyDefine.target, node_name)
            self.control_trans_manager.startTransaction(session_id, request)
            self.info("<control_service> start sync data with node '%s', session [%08X]" %
                      (node_name, session_id))

        if not self.observe_session.has_key(node_name):
            session_id = self.control_trans_manager.allocTransaction(start_observe)
            self.observe_session[node_name] = session_id
            request = getRequest(RequestDefine.invalid)
            request.setString(ParamKeyDefine.target, node_name)
            request.setString(ParamKeyDefine.name, self.node)
            self.control_trans_manager.startTransaction(session_id, request)
            self.info("<control_service> start observe status from node '%s', session [%08X]" %
                      (node_name, session_id))

        # # synch node_client status
        session_id = self.control_trans_manager.allocTransaction(synch_service_status)
        request = getRequest(RequestDefine.invalid)
        request.setString(ParamKeyDefine.target, node_name)
        self.control_trans_manager.startTransaction(session_id, request)

    def onClientDisconnected(self, node_name):
        if self.sync_session.has_key(node_name):
            self.info("<control_service> stop sync data with node '%s', session [%s]" % (
                node_name, self.sync_session[node_name]))
            self.control_trans_manager.terminateTransaction(self.sync_session[node_name])
            del self.sync_session[node_name]

        if self.observe_session.has_key(node_name):
            self.info("<control_service> stop observe status from node '%s', session [%s]" % (
                node_name, self.observe_session[node_name]))
            self.control_trans_manager.terminateTransaction(self.observe_session[node_name])
            del self.observe_session[node_name]

    def handleTimeout(self, event, sender):
        if self.monitor_timer_session == event.session:
            return self.handleMonitorTimeout()
        elif self.status_timer_session == event.session:
            return self.onStatusCheckTimeout()
        elif self.statistic_timer_session == event.session:
            return self.handleStatisticCheckTimeout()
        elif self.synchronize_timer_session == event.session:
            return self.handleSynchronizeTimeout()
        elif self.storage_server_sync_session == event.session:
            return self.handleStorageServerSyncTimeout()
        else:
            self.debug("timeout ignore, session [%08X]" % event.session)

    def handleKeepAlive(self, event, sender):
        if self.statistic_timer_session == event.session:
            return self.handleStatisticKeepAlive()
        else:
            self.debug("keep alive ignore, session [%08X]" % event.session)

    def handleStorageServerSyncTimeout(self):
        with self.storage_server_lock:
            storage_server_list = self.storage_server[:]
        
        if bool(storage_server_list):
            for storage_server in storage_server_list:
                session_id = self.control_trans_manager.allocTransaction(storage_server_sync)
                request = getRequest(RequestDefine.invalid)
                request.setString(ParamKeyDefine.target, storage_server)
                self.control_trans_manager.startTransaction(session_id, request)

    def handleSynchronizeTimeout(self):
        self.synchronizeData()

    def synchronizeData(self):
        self.address_manager.save()
        self.port_manager.save()
        self.forwarder_manager.save()

    def onStatusCheckTimeout(self):
        # #debug
        begin = datetime.datetime.now()

        self.status_manager.checkTimeout()
        # #compute pool status update
        self.updateComputePoolStatus()
        self.updateServerRackStatus()
        self.updateServerRoomStatus()
        self.updateSystemStatus()

        diff = datetime.datetime.now() - begin
        elapse_seconds = diff.seconds + float(diff.microseconds) / 1000000
# #        self.info("<control_service> debug:onStatusCheckTimeout used %.1f second(s)"%(
# #            elapse_seconds))

    def updateComputePoolStatus(self):
        all_pool = self.compute_pool_manager.queryAllPool()
        if 0 != len(all_pool):
            pool_status_list = []
            for compute_pool in all_pool:
                pool_status = ComputePoolStatus()
                pool_status.name = compute_pool.name
                pool_status.uuid = compute_pool.uuid
                host_stop = 0
                host_warning = 0
                host_error = 0
                host_running = 0

                server_stop = 0
                server_running = 0

                cpu_count = 0
                total_cpu_usage = 0.0

                available_memory = 0
                total_memory = 0

                available_disk = 0
                total_disk = 0

                host_list = []

                for resource in compute_pool.resource.values():
                    for host_id in resource.allocated:
                        host_list.append(host_id)
                    # #accumulate server status
                    server_id = resource.server
                    if self.status_manager.containsServerStatus(server_id):
                        server_status = self.status_manager.getServerStatus(server_id)
                        cpu_count += server_status.cpu_count
                        total_cpu_usage += server_status.cpu_count * server_status.cpu_usage
                        available_memory += server_status.memory[0]
                        total_memory += server_status.memory[1]

                        available_disk += server_status.disk_volume[0]
                        total_disk += server_status.disk_volume[1]
                        server_running += 1
                    else:
                        # #server stopped
                        server_stop += 1

                for host_id in host_list:
                    if self.status_manager.containsHostStatus(host_id):
                        host_status = self.status_manager.getHostStatus(host_id)
                        if host_status.status == HostStatusEnum.status_running:
                            host_running += 1
                        elif host_status.status == HostStatusEnum.status_warning:
                            host_warning += 1
                        elif host_status.status == HostStatusEnum.status_error:
                            host_error += 1
                        else:
                            host_stop += 1
                    else:
                        host_error += 1

                pool_status.node = [server_stop, 0, 0, server_running]
                pool_status.host = [host_stop, host_warning, host_error, host_running]
                pool_status.cpu_count = cpu_count
                if 0 != cpu_count:
                    pool_status.cpu_usage = total_cpu_usage / cpu_count

                pool_status.memory = [available_memory, total_memory]
                if 0 != total_memory:
                    pool_status.memory_usage = float(total_memory - available_memory) / total_memory

                pool_status.disk_volume = [available_disk, total_disk]
                if 0 != total_disk:
                    pool_status.disk_usage = float(total_disk - available_disk) / total_disk
                if 0 != host_error:
                    pool_status.status = PoolStatusEnum.error
                elif 0 != host_warning:
                    pool_status.status = PoolStatusEnum.warning
                else:
                    pool_status.status = PoolStatusEnum.running

                pool_status_list.append(pool_status)

            self.status_manager.updateComputePoolStatus(pool_status_list)

    def updateServerRackStatus(self):
        status_list = []
        for server_room in self.config_manager.queryAllServerRooms():
            rack_list = self.config_manager.queryServerRacks(server_room.uuid)
            if 0 != len(rack_list):
                for rack in rack_list:
                    status = ServerRackStatus()
                    status.name = rack.name
                    status.uuid = rack.uuid
                    server_stop = 0
                    server_running = 0

                    cpu_count = 0
                    total_cpu_usage = 0.0

                    for server in self.config_manager.queryServers(rack.uuid):
                        if self.status_manager.containsServerStatus(server.uuid):
                            server_status = self.status_manager.getServerStatus(server.uuid)
                            cpu_count += server_status.cpu_count
                            total_cpu_usage += server_status.cpu_count * server_status.cpu_usage

                            # #memory
                            for index in range(len(server_status.memory)):
                                status.memory[index] += server_status.memory[index]

                            # #disk_volume
                            for index in range(len(server_status.disk_volume)):
                                status.disk_volume[index] += server_status.disk_volume[index]

                            server_running += 1
                            # #disk io
                            for index in range(len(status.disk_io)):
                                status.disk_io[index] += server_status.disk_io[index]

                            # #network io
                            for index in range(len(status.network_io)):
                                status.network_io[index] += server_status.network_io[index]

                            # #network io
                            for index in range(len(status.speed)):
                                status.speed[index] += server_status.speed[index]

                        else:
                            # #server stopped
                            server_stop += 1

                    status.server = [server_stop, 0, 0, server_running]
                    status.cpu_count = cpu_count
                    if 0 != cpu_count:
                        status.cpu_usage = total_cpu_usage / cpu_count

                    total_memory = status.memory[1]
                    if 0 != total_memory:
                        available_memory = status.memory[0]
                        status.memory_usage = float(total_memory - available_memory) / total_memory

                    total_disk = status.disk_volume[1]
                    if 0 != total_disk:
                        available_disk = status.disk_volume[0]
                        status.disk_usage = float(total_disk - available_disk) / total_disk

                    if 0 == server_running:
                        status.status = StatusEnum.stop
                    else:
                        status.status = StatusEnum.running

                    status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    status_list.append(status)
                # #end for rack in rack_list:
        # #end for server_room in self.config_manager.queryAllServerRooms():
        if 0 != len(status_list):
            self.status_manager.updateServerRackStatus(status_list)

    def updateServerRoomStatus(self):
        status_list = []
        for server_room in self.config_manager.queryAllServerRooms():
            status = ServerRoomStatus()
            status.name = server_room.name
            status.uuid = server_room.uuid

            cpu_count = 0
            total_cpu_usage = 0.0

            rack_list = self.config_manager.queryServerRacks(server_room.uuid)
            for rack in rack_list:
                if self.status_manager.containsServerRackStatus(rack.uuid):
                    rack_status = self.status_manager.getServerRackStatus(rack.uuid)
                    cpu_count += rack_status.cpu_count
                    total_cpu_usage += rack_status.cpu_count * rack_status.cpu_usage
                    # #memory
                    for index in range(len(rack_status.memory)):
                        status.memory[index] += rack_status.memory[index]

                    # #disk_volume
                    for index in range(len(rack_status.disk_volume)):
                        status.disk_volume[index] += rack_status.disk_volume[index]

                    # #server
                    for index in range(len(rack_status.server)):
                        status.server[index] += rack_status.server[index]

                    # #disk io
                    for index in range(len(status.disk_io)):
                        status.disk_io[index] += rack_status.disk_io[index]

                    # #network io
                    for index in range(len(status.network_io)):
                        status.network_io[index] += rack_status.network_io[index]

                    # #network io
                    for index in range(len(status.speed)):
                        status.speed[index] += rack_status.speed[index]

            status.cpu_count = cpu_count
            if 0 != cpu_count:
                status.cpu_usage = total_cpu_usage / cpu_count

            total_memory = status.memory[1]
            if 0 != total_memory:
                available_memory = status.memory[0]
                status.memory_usage = float(total_memory - available_memory) / total_memory

            total_disk = status.disk_volume[1]
            if 0 != total_disk:
                available_disk = status.disk_volume[0]
                status.disk_usage = float(total_disk - available_disk) / total_disk

            if 0 != status.server[2]:
                status.status = StatusEnum.error
            elif 0 != status.server[1]:
                status.status = StatusEnum.warning
            elif 0 == status.server[3]:
                status.status = StatusEnum.stop
            else:
                status.status = StatusEnum.running

            status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_list.append(status)

        # #end for server_room in self.config_manager.queryAllServerRooms():
        if 0 != len(status_list):
            self.status_manager.updateServerRoomStatus(status_list)

    def updateSystemStatus(self):
        status = SystemStatus()
        # #host
        for pool_status in self.status_manager.getAllComputePoolStatus():
            # #host
            for index in range(len(pool_status.host)):
                status.host[index] += pool_status.host[index]

        cpu_count = 0
        total_cpu_usage = 0.0

        for room_status in self.status_manager.getAllServerRoomStatus():
            cpu_count += room_status.cpu_count
            total_cpu_usage += room_status.cpu_count * room_status.cpu_usage

            # #memory
            for index in range(len(room_status.memory)):
                status.memory[index] += room_status.memory[index]

            # #disk_volume
            for index in range(len(room_status.disk_volume)):
                status.disk_volume[index] += room_status.disk_volume[index]

            # #server
            for index in range(len(room_status.server)):
                status.server[index] += room_status.server[index]

            # #disk io
            for index in range(len(status.disk_io)):
                status.disk_io[index] += room_status.disk_io[index]

            # #network io
            for index in range(len(status.network_io)):
                status.network_io[index] += room_status.network_io[index]

            # #network io
            for index in range(len(status.speed)):
                status.speed[index] += room_status.speed[index]

        status.cpu_count = cpu_count
        if 0 != cpu_count:
            status.cpu_usage = total_cpu_usage / cpu_count

        total_memory = status.memory[1]
        if 0 != total_memory:
            available_memory = status.memory[0]
            status.memory_usage = float(total_memory - available_memory) / total_memory

        total_disk = status.disk_volume[1]
        if 0 != total_disk:
            available_disk = status.disk_volume[0]
            status.disk_usage = float(total_disk - available_disk) / total_disk

        if 0 != status.server[2]:
            status.status = StatusEnum.error
        elif 0 != status.server[1]:
            status.status = StatusEnum.warning
        elif 0 == status.server[3]:
            status.status = StatusEnum.stop
        else:
            status.status = StatusEnum.running

        status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.status_manager.updateSystemStatus(status)

    def handleMonitorTimeout(self):
        begin = datetime.datetime.now()
        # #clear all timeout task
        self.monitor_manager.checkTimeout()

        # #invoke notify monitor data
        for monitor in self.monitor_manager.getAllMonitor():
            if 0 != len(monitor.listener_list):
                # #monito enabled
                if MonitorLevel.system == monitor.level:
                    self.notifySystemMonitorData(monitor)
                elif MonitorLevel.server_room == monitor.level:
                    self.notifyServerRoomMonitorData(monitor)
                elif MonitorLevel.server_rack == monitor.level:
                    self.notifyServerRackMonitorData(monitor)
                elif MonitorLevel.server == monitor.level:
                    self.notifyServerMonitorData(monitor)
                elif MonitorLevel.compute_node == monitor.level:
                    self.notifyComputeNodeMonitorData(monitor)
                elif MonitorLevel.host == monitor.level:
                    self.notifyHostMonitorData(monitor)

        diff = datetime.datetime.now() - begin
        elapse_seconds = diff.seconds + float(diff.microseconds) / 1000000
# #        self.info("<control_service> debug:handleMonitorTimeout used %.1f second(s)"%(
# #            elapse_seconds))

    def notifySystemMonitorData(self, monitor):
        if not self.status_manager.containsSystemStatus():
            return
        status = self.status_manager.getSystemStatus()

        # #pack message
        for task_id in monitor.listener_list:
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            event.setUIntArray(ParamKeyDefine.server, status.server)
            event.setUIntArray(ParamKeyDefine.host, status.host)
            event.setUInt(ParamKeyDefine.cpu_count, status.cpu_count)
            event.setFloat(ParamKeyDefine.cpu_usage, status.cpu_usage)
            event.setUIntArray(ParamKeyDefine.memory, status.memory)
            event.setFloat(ParamKeyDefine.memory_usage, status.memory_usage)
            event.setUIntArray(ParamKeyDefine.disk_volume, status.disk_volume)
            event.setFloat(ParamKeyDefine.disk_usage, status.disk_usage)
            event.setUIntArray(ParamKeyDefine.disk_io, status.disk_io)
            event.setUIntArray(ParamKeyDefine.network_io, status.network_io)
            event.setUIntArray(ParamKeyDefine.speed, status.speed)
            event.setString(ParamKeyDefine.timestamp, status.timestamp)

            self.sendMessage(event, task.receive_node)

    def notifyServerRoomMonitorData(self, monitor):
        if 0 == len(monitor.listener_list):
            # #no target
            return
        # #build dispatch map
        dispatch_map = {}
        for listener_id in monitor.listener_list:
            dispatch_map[listener_id] = []

        for target_id in monitor.target_map.keys():
            if self.status_manager.containsServerRoomStatus(target_id):
                status = self.status_manager.getServerRoomStatus(target_id)
                for listener_id in monitor.target_map[target_id]:
                    dispatch_map[listener_id].append(status)

        for status in self.status_manager.getAllServerRoomStatus():
            for listener_id in monitor.global_listener:
                dispatch_map[listener_id].append(status)

        # #pack message
        for task_id in dispatch_map.keys():
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            uuid = []
            server = []
            cpu_count = []
            cpu_usage = []
            memory = []
            memory_usage = []
            disk_volume = []
            disk_usage = []
            disk_io = []
            network_io = []
            speed = []
            timestamp = []

            for status in dispatch_map[task_id]:
                uuid.append(status.uuid)
                server.append(status.server)
                cpu_count.append(status.cpu_count)
                cpu_usage.append(status.cpu_usage)
                memory.append(status.memory)
                memory_usage.append(status.memory_usage)
                disk_volume.append(status.disk_volume)
                disk_usage.append(status.disk_usage)
                disk_io.append(status.disk_io)
                network_io.append(status.network_io)
                speed.append(status.speed)
                timestamp.append(status.timestamp)

            event.setStringArray(ParamKeyDefine.uuid, uuid)
            event.setUIntArrayArray(ParamKeyDefine.server, server)
            event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
            event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
            event.setUIntArrayArray(ParamKeyDefine.memory, memory)
            event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
            event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
            event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
            event.setUIntArrayArray(ParamKeyDefine.speed, speed)
            event.setStringArray(ParamKeyDefine.timestamp, timestamp)

            self.sendMessage(event, task.receive_node)

    def notifyServerRackMonitorData(self, monitor):
        if 0 == len(monitor.listener_list):
            # #no target
            return
        # #build dispatch map
        dispatch_map = {}
        for listener_id in monitor.listener_list:
            dispatch_map[listener_id] = []

        for target_id in monitor.target_map.keys():
            if self.status_manager.containsServerRackStatus(target_id):
                status = self.status_manager.getServerRackStatus(target_id)
                for listener_id in monitor.target_map[target_id]:
                    dispatch_map[listener_id].append(status)

        for status in self.status_manager.getAllServerRackStatus():
            for listener_id in monitor.global_listener:
                dispatch_map[listener_id].append(status)

        # #pack message
        for task_id in dispatch_map.keys():
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            uuid = []
            server = []
            cpu_count = []
            cpu_usage = []
            memory = []
            memory_usage = []
            disk_volume = []
            disk_usage = []
            disk_io = []
            network_io = []
            speed = []
            timestamp = []

            for status in dispatch_map[task_id]:
                uuid.append(status.uuid)
                server.append(status.server)
                cpu_count.append(status.cpu_count)
                cpu_usage.append(status.cpu_usage)
                memory.append(status.memory)
                memory_usage.append(status.memory_usage)
                disk_volume.append(status.disk_volume)
                disk_usage.append(status.disk_usage)
                disk_io.append(status.disk_io)
                network_io.append(status.network_io)
                speed.append(status.speed)
                timestamp.append(status.timestamp)

            event.setStringArray(ParamKeyDefine.uuid, uuid)
            event.setUIntArrayArray(ParamKeyDefine.server, server)
            event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
            event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
            event.setUIntArrayArray(ParamKeyDefine.memory, memory)
            event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
            event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
            event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
            event.setUIntArrayArray(ParamKeyDefine.speed, speed)
            event.setStringArray(ParamKeyDefine.timestamp, timestamp)

            self.sendMessage(event, task.receive_node)

    def notifyServerMonitorData(self, monitor):
        if 0 == len(monitor.listener_list):
            # #no target
            return
        # #build dispatch map
        dispatch_map = {}
        for listener_id in monitor.listener_list:
            dispatch_map[listener_id] = []

        for target_id in monitor.target_map.keys():
            if self.status_manager.containsServerStatus(target_id):
                status = self.status_manager.getServerStatus(target_id)
                for listener_id in monitor.target_map[target_id]:
                    dispatch_map[listener_id].append(status)

        for status in self.status_manager.getAllServerStatus():
            for listener_id in monitor.global_listener:
                dispatch_map[listener_id].append(status)

        # #pack message
        for task_id in dispatch_map.keys():
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            uuid = []
            cpu_count = []
            cpu_usage = []
            memory = []
            memory_usage = []
            disk_volume = []
            disk_usage = []
            disk_io = []
            network_io = []
            speed = []
            timestamp = []
            status = []

            for server_status in dispatch_map[task_id]:
                uuid.append(server_status.uuid)
                cpu_count.append(server_status.cpu_count)
                cpu_usage.append(server_status.cpu_usage)
                memory.append(server_status.memory)
                memory_usage.append(server_status.memory_usage)
                disk_volume.append(server_status.disk_volume)
                disk_usage.append(server_status.disk_usage)
                disk_io.append(server_status.disk_io)
                network_io.append(server_status.network_io)
                speed.append(server_status.speed)
                timestamp.append(server_status.timestamp)
                status.append(server_status.status)

            event.setStringArray(ParamKeyDefine.uuid, uuid)
            event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
            event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
            event.setUIntArrayArray(ParamKeyDefine.memory, memory)
            event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
            event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
            event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
            event.setUIntArrayArray(ParamKeyDefine.speed, speed)
            event.setStringArray(ParamKeyDefine.timestamp, timestamp)
            event.setUIntArray(ParamKeyDefine.status, status)

            self.sendMessage(event, task.receive_node)

    def notifyComputeNodeMonitorData(self, monitor):
        if 0 == len(monitor.listener_list):
            # #no target
            return
        # #build dispatch map
        dispatch_map = {}
        for listener_id in monitor.listener_list:
            dispatch_map[listener_id] = []

        for target_id in monitor.target_map.keys():
            contain_resource, pool_id = self.compute_pool_manager.searchResource(target_id)
            if not contain_resource:
                continue
            resource = self.compute_pool_manager.getResource(pool_id, target_id)
            for listener_id in monitor.target_map[target_id]:
                dispatch_map[listener_id].append(resource)

        for pool in self.compute_pool_manager.queryAllPool():
            for resource in self.compute_pool_manager.queryResource(pool.uuid):
                for listener_id in monitor.global_listener:
                    dispatch_map[listener_id].append(resource)

        # #pack message
        for task_id in dispatch_map.keys():
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            name = []
            count = []
            cpu_count = []
            cpu_usage = []
            memory = []
            memory_usage = []
            disk_volume = []
            disk_usage = []
            disk_io = []
            network_io = []
            speed = []
            timestamp = []
            status = []

            for resource in dispatch_map[task_id]:
                if not self.status_manager.containsServerStatus(resource.server):
                    continue
                node_status = self.status_manager.getServerStatus(resource.server)

                name.append(resource.name)
                # #allocated cloud host
                count.append(len(resource.allocated))

                cpu_count.append(node_status.cpu_count)
                cpu_usage.append(node_status.cpu_usage)
                memory.append(node_status.memory)
                memory_usage.append(node_status.memory_usage)
                disk_volume.append(node_status.disk_volume)
                disk_usage.append(node_status.disk_usage)
                disk_io.append(node_status.disk_io)
                network_io.append(node_status.network_io)
                speed.append(node_status.speed)
                timestamp.append(node_status.timestamp)
                status.append(node_status.status)

            event.setStringArray(ParamKeyDefine.name, name)
            event.setUIntArray(ParamKeyDefine.count, count)
            event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
            event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
            event.setUIntArrayArray(ParamKeyDefine.memory, memory)
            event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
            event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
            event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
            event.setUIntArrayArray(ParamKeyDefine.speed, speed)
            event.setStringArray(ParamKeyDefine.timestamp, timestamp)
            event.setUIntArray(ParamKeyDefine.status, status)

            self.sendMessage(event, task.receive_node)

    def notifyHostMonitorData(self, monitor):
        if 0 == len(monitor.listener_list):
            # #no target
            return
        # #build dispatch map
        dispatch_map = {}
        for listener_id in monitor.listener_list:
            dispatch_map[listener_id] = []

        for target_id in monitor.target_map.keys():
            if self.status_manager.containsHostStatus(target_id):
                status = self.status_manager.getHostStatus(target_id)
            else:
                if not self.config_manager.containsHost(target_id):
                    continue
                host_info = self.config_manager.getHost(target_id)
                status = HostStatus()
                status.uuid = target_id
                status.cpu_count = host_info.cpu_count
                status.memory = [host_info.memory, host_info.memory]
                status.disk_volume = host_info.disk_volume
                status.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status.status = HostStatusEnum.status_error

            for listener_id in monitor.target_map[target_id]:
                dispatch_map[listener_id].append(status)

        for status in self.status_manager.getAllHostStatus():
            for listener_id in monitor.global_listener:
                dispatch_map[listener_id].append(status)

        # #pack message
        for task_id in dispatch_map.keys():
            task = self.monitor_manager.getTask(task_id)
            event = getEvent(EventDefine.monitor_data)
            event.success = True
            event.session = task.receive_session
            setUInt(event, ParamKeyDefine.task, task.task_id)
            setUInt(event, ParamKeyDefine.level, task.monitor_level)

            uuid = []
            cpu_count = []
            cpu_usage = []
            memory = []
            memory_usage = []
            disk_volume = []
            disk_usage = []
            disk_io = []
            network_io = []
            speed = []
            timestamp = []
            status = []

            for host_status in dispatch_map[task_id]:
                uuid.append(host_status.uuid)
                cpu_count.append(host_status.cpu_count)
                cpu_usage.append(host_status.cpu_usage)
                memory.append(host_status.memory)
                memory_usage.append(host_status.memory_usage)
                disk_volume.append(host_status.disk_volume)
                disk_usage.append(host_status.disk_usage)
                disk_io.append(host_status.disk_io)
                network_io.append(host_status.network_io)
                speed.append(host_status.speed)
                timestamp.append(host_status.timestamp)
                status.append(host_status.status)

            event.setStringArray(ParamKeyDefine.uuid, uuid)
            event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
            event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
            event.setUIntArrayArray(ParamKeyDefine.memory, memory)
            event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
            event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
            event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
            event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
            event.setUIntArrayArray(ParamKeyDefine.speed, speed)
            event.setStringArray(ParamKeyDefine.timestamp, timestamp)
            event.setUIntArray(ParamKeyDefine.status, status)

            self.sendMessage(event, task.receive_node)


    def handleStartMonitorRequest(self, request, sender):
        task = MonitorTask()
        task.receive_node = sender
        task.receive_session = request.session
        task.target_list = getStringArray(request, ParamKeyDefine.target)
        task.monitor_level = getUInt(request, ParamKeyDefine.level)
        task.timeout_count = 0
        self.info("<control_service> receive start monitor request from '%s', request session [%08X], monitor level %d" % (
            task.receive_node, task.receive_session, task.monitor_level))
        response = getResponse(RequestDefine.start_monitor)
        response.session = request.session

        if not task.target_list:
            task.global_monitor = True
        elif task.monitor_level == MonitorLevel.server_room:
            # #server room
            for room_id in task.target_list:
                if not self.config_manager.containsServerRoom(room_id):
                    self.error("<control_service> start monitor fail, invalid target server room '%s'" % (
                        room_id))
                    self.sendMessage(response, sender)
                    return False

        elif task.monitor_level == MonitorLevel.server_rack:
            # #server rack
            for rack_id in task.target_list:
                if not self.config_manager.containsServerRack(rack_id):
                    self.error("<control_service> start monitor fail, invalid target server rack '%s'" % (
                        rack_id))
                    self.sendMessage(response, sender)
                    return False
        elif task.monitor_level == MonitorLevel.server:
            # #server
            for server_id in task.target_list:
                if not self.config_manager.containsServer(server_id):
                    self.error("<control_service> start monitor fail, invalid target server '%s'" % (
                        server_id))
                    self.sendMessage(response, sender)
                    return False

        elif task.monitor_level == MonitorLevel.compute_node:
            # #compute_node
            for resource_name in task.target_list:
                contains_resource, pool_id = self.compute_pool_manager.searchResource(resource_name)
                if not contains_resource:
                    self.error("<control_service> start monitor fail, invalid target compute resource '%s'" % (
                        resource_name))
                    self.sendMessage(response, sender)
                    return False
        elif task.monitor_level == MonitorLevel.host:
            # #host
            for host_id in task.target_list:
                if not self.config_manager.containsHost(host_id):
                    self.error("<control_service> start monitor fail, invalid target host '%s'" % (
                        host_id))
                    self.sendMessage(response, sender)
                    return False

        if self.monitor_manager.addTask(task):
            self.info("<control_service> alloc monitor task success, task id %d" % task.task_id)
            response.success = True
            setUInt(response, ParamKeyDefine.task, task.task_id)
        else:
            self.error("<control_service> alloc monitor task fail")

        self.sendMessage(response, sender)

    def handleStopMonitorRequest(self, request, sender):
        task_id = getUInt(request, ParamKeyDefine.task)
        response = getResponse(RequestDefine.stop_monitor)
        if self.monitor_manager.removeTask(task_id):
            self.info("<control_service> dealloc monitor task %d success" % (task_id))
            response.success = True
        else:
            self.warn("<control_service> dealloc monitor task %d fail" % (task_id))
            response.success = False
        response.session = request.session
        self.sendMessage(response, sender)

    def handleMonitorHeartBeat(self, event, sender):
        task_id = getUInt(event, ParamKeyDefine.task)
        self.monitor_manager.processHeartBeat(task_id)

    def onDataServerConnected(self, node_name):
        # #load service
        session_id = self.control_trans_manager.allocTransaction(load_service)
        request = getRequest(RequestDefine.invalid)
        setString(request, ParamKeyDefine.target, node_name)
        self.control_trans_manager.startTransaction(session_id, request)

        # #load config
        session_id = self.control_trans_manager.allocTransaction(load_config)
        request = getRequest(RequestDefine.invalid)
        setString(request, ParamKeyDefine.target, node_name)
        self.control_trans_manager.startTransaction(session_id, request)

    def sendToStorageServer(self, msg):
        with self.storage_server_lock:
            if bool(self.storage_server):
                self.sendMessage(msg, self.storage_server[-1])
                
    def getStorageServer(self):
        with self.storage_server_lock:
            if bool(self.storage_server):
                return self.storage_server[-1]
            
            return None

    def handleStartStatisticRequest(self, request, sender):
        self.info("receive start statistic request from '%s'" % sender)
        self.info("start statistic, server '%s', data update interval %d second(s)" % (
            sender, self.statistic_timer_interval))
# #        self.info("%d phycical host(s), %d virtual domain(s) available"%(
# #            len(host_list), len(domain_list)))
        self.console("start statistic, server '%s', data update interval %d second(s)" % (
            sender, self.statistic_timer_interval))
# #        self.console("%d phycical host(s), %d virtual domain(s) available"%(
# #            len(host_list), len(domain_list)))

        self.statistic_timer_id = self.setLoopTimer(self.statistic_timer_interval,
                                                    self.statistic_timer_session)
        self.statistic_timeout = 0

        self.statistic_server = sender

        response = getResponse(RequestDefine.start_statistic)
        response.success = True
        response.session = self.statistic_timer_session
        self.sendMessage(response, sender)

        self.reportStatisticData()


    def handleStopStatisticRequest(self, request, sender):
        self.info("stop statistic from server '%s'" % (sender))
        self.console("stop statistic from server '%s'" % (sender))
        response = getResponse(RequestDefine.stop_statistic)
        if 0 != self.statistic_timer_id:
            self.clearTimer(self.statistic_timer_id)
            response.success = True
            self.statistic_timer_id = 0

        self.statistic_server = ""
        self.sendMessage(response, sender)

    def handleStatisticCheckTimeout(self):
        self.statistic_timeout += 1
        if self.statistic_timeout >= self.max_statistic_timeout:
            self.warn("warning:statistic timeout, stop statistic for server '%s'" % (self.statistic_server))
            self.console("warning:statistic timeout, stop statistic for server '%s'" % (self.statistic_server))
            self.clearTimer(self.statistic_timer_id)
            self.statistic_timer_id = 0
            return
        self.reportStatisticData()

    def reportStatisticData(self):
        self.notifyPhysicalStatisticData()
        self.notifyVirtualStatisticData()

    def notifyPhysicalStatisticData(self):
        # #physical/server
        event = getEvent(EventDefine.statistic_data)
        event.setUInt(ParamKeyDefine.level, 0)  # #level - 0, physical nodes
        uuid = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        disk_io = []
        network_io = []
        speed = []
        timestamp = []
        status = []

        server_list = self.status_manager.getAllServerStatus()
        for server_status in server_list:
            uuid.append(server_status.uuid)
            cpu_count.append(server_status.cpu_count)
            cpu_usage.append(server_status.cpu_usage)
            memory.append(server_status.memory)
            memory_usage.append(server_status.memory_usage)
            disk_volume.append(server_status.disk_volume)
            disk_usage.append(server_status.disk_usage)
            disk_io.append(server_status.disk_io)
            network_io.append(server_status.network_io)
            speed.append(server_status.speed)
            timestamp.append(server_status.timestamp)
            status.append(server_status.status)

        event.setStringArray(ParamKeyDefine.uuid, uuid)
        event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
        event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
        event.setUIntArrayArray(ParamKeyDefine.memory, memory)
        event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
        event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
        event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
        event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
        event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
        event.setUIntArrayArray(ParamKeyDefine.speed, speed)
        event.setStringArray(ParamKeyDefine.timestamp, timestamp)
        event.setUIntArray(ParamKeyDefine.status, status)

        self.sendMessage(event, self.statistic_server)
        
        self.debug("<control_service> notify physical statistic data : uuid '%s', cpu_count '%s', cpu_usage '%s', memory '%s', memory_usage '%s', disk_volume '%s', disk_usage '%s', disk_io '%s', network_io '%s', speed '%s', timestamp '%s', status '%s'" %
                   (uuid, cpu_count, cpu_usage, memory, memory_usage, disk_volume, disk_usage, disk_io, network_io, speed, timestamp, status))

    def notifyVirtualStatisticData(self):
        # #virtual/host
        event = getEvent(EventDefine.statistic_data)
        event.setUInt(ParamKeyDefine.level, 1)  # #level - 1, virtual nodes
        uuid = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        disk_io = []
        network_io = []
        speed = []
        timestamp = []
        status = []

        host_list = self.status_manager.getAllHostStatus()
        for host_status in host_list:
            uuid.append(host_status.uuid)
            cpu_count.append(host_status.cpu_count)
            cpu_usage.append(host_status.cpu_usage)
            memory.append(host_status.memory)
            memory_usage.append(host_status.memory_usage)
            disk_volume.append(host_status.disk_volume)
            disk_usage.append(host_status.disk_usage)
            disk_io.append(host_status.disk_io)
            network_io.append(host_status.network_io)
            speed.append(host_status.speed)
            timestamp.append(host_status.timestamp)
            status.append(host_status.status)

        event.setStringArray(ParamKeyDefine.uuid, uuid)
        event.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
        event.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
        event.setUIntArrayArray(ParamKeyDefine.memory, memory)
        event.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
        event.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
        event.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
        event.setUIntArrayArray(ParamKeyDefine.disk_io, disk_io)
        event.setUIntArrayArray(ParamKeyDefine.network_io, network_io)
        event.setUIntArrayArray(ParamKeyDefine.speed, speed)
        event.setStringArray(ParamKeyDefine.timestamp, timestamp)
        event.setUIntArray(ParamKeyDefine.status, status)

        self.sendMessage(event, self.statistic_server)
        
        self.debug("<control_service> notify virtual statistic data : uuid '%s', cpu_count '%s', cpu_usage '%s', memory '%s', memory_usage '%s', disk_volume '%s', disk_usage '%s', disk_io '%s', network_io '%s', speed '%s', timestamp '%s', status '%s'" %
                   (uuid, cpu_count, cpu_usage, memory, memory_usage, disk_volume, disk_usage, disk_io, network_io, speed, timestamp, status))

    def handleStatisticKeepAlive(self):
        self.statistic_timeout = 0

    def onStatisticServerDisconnected(self, node_name):
        if node_name != self.statistic_server:
            return
        if 0 != self.statistic_timer_id:
            self.info("statistic timer %d cleared" % (self.statistic_timer_id))
            self.clearTimer(self.statistic_timer_id)
            self.statistic_timer_id = 0

        self.info("statistic server disconnected, stop report for server '%s'" % (node_name))
        self.console("statistic server disconnected, stop report for server '%s'" % (node_name))
        self.statistic_server = ""

    def handleServiceStatusChanged(self, event, sender):
        service = ServiceStatus()
        service.name = event.getString(ParamKeyDefine.name)
        service.type = event.getUInt(ParamKeyDefine.type)
        service.group = event.getString(ParamKeyDefine.group)
        service.ip = event.getString(ParamKeyDefine.ip)
        service.port = event.getUInt(ParamKeyDefine.port)
        service.version = event.getString(ParamKeyDefine.version)
        service.server = event.getString(ParamKeyDefine.server)
        service.status = event.getUInt(ParamKeyDefine.status)

        if service.isRunning():
            self.service_manager.activeService(service)
            self.info("<control_service> service actived, name '%s'(%s:%d)" % (service.name, service.ip, service.port))

        elif service.isStopped():
            self.service_manager.deactiveService(service.name)
            self.info("<control_service> service deactived, name '%s'(%s:%d)" % (service.name, service.ip, service.port))



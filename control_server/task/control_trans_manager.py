#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.transaction_manager import *
from task_type import *
from task_session import *
from load_config import *
from load_service import *
from initial_node import *
from initial_storage import *

from query_address_pool import *
from create_address_pool import *
from delete_address_pool import *
from add_address_resource import *
from remove_address_resource import *
from query_address_resource import *

from query_port_pool import *
from create_port_pool import *
from delete_port_pool import *
from add_port_resource import *
from remove_port_resource import *
from query_port_resource import *

from query_compute_pool import *
from create_compute_pool import *
from modify_compute_pool import *
from delete_compute_pool import *
from add_compute_resource import *
from remove_compute_resource import *
from query_compute_resource import *

from query_storage_pool import *
from create_storage_pool import *
from delete_storage_pool import *
from add_storage_resource import *
from remove_storage_resource import *
from query_storage_resource import *

from query_server_room import *
from create_server_room import *
from delete_server_room import *
from modify_server_room import *

from query_server_rack import *
from create_server_rack import *
from delete_server_rack import *
from modify_server_rack import *

from query_server import *
from add_server import *
from remove_server import *
from modify_server import *

from query_service_type import *
from query_service_group import *
from query_service import *

from create_host import *
from modify_host import *
from delete_host import *
from start_host import *
from stop_host import *
from halt_host import *
from restart_host import *
from query_host import *
from query_host_info import *
from resume_host import *

from query_iso_image import *
from upload_iso_image import *
from modify_iso_image import *
from delete_iso_image import *

from insert_media import *
from change_media import *
from eject_media import *

from query_whisper import *

from query_disk_image import *
from modify_disk_image import *
from delete_disk_image import *
from create_disk_image import *

from query_application import *
from query_resource_pool import *
from query_struct import *

from set_forwarder_status import *
from query_forwarder_summary import *
from query_forwarder import *
from get_forwarder import *
from add_forwarder import *
from remove_forwarder import *

from check_config import *

from attach_disk import *
from detach_disk import *
from start_observe import *
from task.modify_storage_pool import ModifyStoragePoolTask
from task.initial_storage_pool import InitialStoragePoolTask
from task.initial_storage_resource import InitialStorageResourceTask
from task.initial_device import InitialDeviceTask
from task.query_device import QueryDeviceTask
from task.create_device import CreateDeviceTask
from task.modify_device import ModifyDeviceTask
from task.delete_device import DeleteDeviceTask
from task.create_network import CreateNetworkTask
from task.modify_network import ModifyNetworkTask
from task.query_network import QueryNetworkTask
from task.query_network_detail import QueryNetworkDetailTask
from task.delete_network import DeleteNetworkTask
from task.start_network import StartNetworkTask
from task.stop_network import StopNetworkTask
from task.attach_host import AttachHostTask
from task.detach_host import DetachHostTask
from task.network_attach_address import NetworkAttachAddressTask
from task.network_detach_address import NetworkDetachAddressTask
from task.network_bind_port import NetworkBindPortTask
from task.network_unbind_port import NetworkUnbindPortTask
from task.query_network_host import QueryNetworkHostTask
from task.create_snapshot_pool import CreateSnapshotPoolTask
from task.delete_snapshot_pool import DeleteSnapshotPoolTask
from task.add_snapshot_node import AddSnapshotNodeTask
from task.remove_snapshot_node import RemoveSnapshotNodeTask
from task.query_snapshot_pool import QuerySnapshotPoolTask
from task.modify_snapshot_pool import ModifySnapshotPoolTask
from task.query_snapshot_node import QuerySnapshotNodeTask
from task.query_snapshot import QuerySnapshotTask
from task.create_snapshot import CreateSnapshotTask
from task.delete_snapshot import DeleteSnapshotTask
from task.resume_snapshot import ResumeSnapshotTask
from task.initial_snapshot_pool import InitialSnapshotPoolTask
from task.initial_snapshot_node import InitialSnapshotNodeTask
from task.flush_disk_image import FlushDiskImageTask
from task.backup_host import BackupHostTask
from task.resume_backup import ResumeBackupTask
from task.query_host_backup import QueryHostBackupTask
from task.add_rule import AddRuleTask
from task.remove_rule import RemoveRuleTask
from task.query_rule import QueryRuleTask
from task.query_operate_detail import QueryOperateDetailTask
from task.query_operate_summary import QueryOperateSummaryTask
from task.query_service_detail import QueryServiceDetailTask
from task.query_service_summary import QueryServiceSummaryTask
from task.reset_host import ResetHostTask
from task.query_compute_pool_detail import QueryComputePoolDetailTask
from task.query_storage_device import QueryStorageDeviceTask
from task.add_storage_device import AddStorageDeviceTask
from task.remove_storage_device import RemoveStorageDeviceTask
from task.enable_storage_device import EnableStorageDeviceTask
from task.disable_storage_device import DisableStorageDeviceTask
from task.modify_service import ModifyServiceTask
from task.storage_server_sync import StorageServerSyncTask
from task.synch_service_status import SyncServiceStatusTask


class ControlTransManager(TransactionManager):
    
    min_session_id = 1000
    session_count = 100
    
    def __init__(self, logger_name, message_handler,
                 status_manager, config_manager, iso_manager,
                 compute_pool_manager, storage_pool_manager,
                 address_manager, port_manager,
                 service_manager, image_manager,
                 forwarder_manager, expire_manager,
                 network_manager, snapshot_pool_manager,
                 work_thread):
        
        TransactionManager.__init__(self, logger_name, self.min_session_id,
                                    self.session_count, work_thread)

        ##system query
        self.addTask(query_application,
                     QueryApplicationTask(query_application, message_handler,
                                          status_manager,
                                          iso_manager,
                                          image_manager))

        self.addTask(query_resource_pool,
                     QueryResourcePoolTask(query_resource_pool, message_handler,
                                           status_manager,
                                           compute_pool_manager,
                                           storage_pool_manager,
                                           address_manager,
                                           port_manager))

        self.addTask(query_struct,
                     QueryStructTask(query_struct, message_handler,
                                     status_manager,
                                     service_manager))

        ##add task        
        self.addTask(load_service,
                     LoadServiceTask(load_service, message_handler,
                                    service_manager))
        self.addTask(load_config,
                     LoadConfigTask(load_config, message_handler,
                                    config_manager))
        self.addTask(initial_node,
                     InitialNodeTask(initial_node, message_handler,
                                     config_manager, compute_pool_manager,
                                     address_manager, port_manager,
                                     forwarder_manager, expire_manager))
        
        self.addTask(resume_host,
                     ResumeHostTask(resume_host, message_handler,
                                    config_manager, compute_pool_manager,
                                    address_manager, port_manager,
                                    forwarder_manager))

        self.addTask(initial_storage,
                     InitialStorageTask(initial_storage, message_handler,
                                        iso_manager, service_manager,
                                        image_manager))


        """
        define for 2.0
        """
        ##address pool
        self.addTask(query_address_pool,
                     QueryAddressPoolTask(query_address_pool, message_handler,
                                          address_manager))
        
        self.addTask(create_address_pool,
                     CreateAddressPoolTask(create_address_pool, message_handler,
                                          address_manager))
        
        self.addTask(delete_address_pool,
                     DeleteAddressPoolTask(delete_address_pool, message_handler,
                                          address_manager, compute_pool_manager, network_manager))
        
        self.addTask(add_address_resource,
                     AddAddressResourceTask(add_address_resource, message_handler,
                                          address_manager))
        
        self.addTask(remove_address_resource,
                     RemoveAddressResourceTask(remove_address_resource, message_handler,
                                          address_manager))
        
        self.addTask(query_address_resource,
                     QueryAddressResourceTask(query_address_resource, message_handler,
                                          address_manager))

        ##port pool
        self.addTask(query_port_pool,
                     QueryPortPoolTask(query_port_pool, message_handler,
                                          port_manager))
        
        self.addTask(create_port_pool,
                     CreatePortPoolTask(create_port_pool, message_handler,
                                          port_manager))
        
        self.addTask(delete_port_pool,
                     DeletePortPoolTask(delete_port_pool, message_handler,
                                          port_manager, compute_pool_manager))
        
        self.addTask(add_port_resource,
                     AddPortResourceTask(add_port_resource, message_handler,
                                          port_manager))
        
        self.addTask(remove_port_resource,
                     RemovePortResourceTask(remove_port_resource, message_handler,
                                          port_manager))
        
        self.addTask(query_port_resource,
                     QueryPortResourceTask(query_port_resource, message_handler,
                                          port_manager))
        
        #-----------------
        
        ##storage pool
        self.addTask(initial_storage_pool,
                     InitialStoragePoolTask(initial_storage_pool, message_handler, self,
                                          storage_pool_manager))
        
        
        self.addTask(query_storage_pool,
                     QueryStoragePoolTask(query_storage_pool, message_handler,
                                          storage_pool_manager))
        
        self.addTask(create_storage_pool,
                     CreateStoragePoolTask(create_storage_pool, message_handler,
                                          storage_pool_manager))
        
        self.addTask(modify_storage_pool,
                     ModifyStoragePoolTask(modify_storage_pool, message_handler,
                                          storage_pool_manager))
        
        self.addTask(delete_storage_pool,
                     DeleteStoragePoolTask(delete_storage_pool, message_handler,
                                          storage_pool_manager))
        
        #---------------------
        
        self.addTask(initial_storage_resource,
                     InitialStorageResourceTask(initial_storage_resource, message_handler,
                                          storage_pool_manager))
        
        self.addTask(add_storage_resource,
                     AddStorageResourceTask(add_storage_resource, message_handler,
                                          storage_pool_manager))
        
        self.addTask(remove_storage_resource,
                     RemoveStorageResourceTask(remove_storage_resource, message_handler,
                                          storage_pool_manager))
        
        self.addTask(query_storage_resource,
                     QueryStorageResourceTask(query_storage_resource, message_handler,
                                          storage_pool_manager))
        
        #---------------------------
        
        # about device
        
        self.addTask(initial_device,
                     InitialDeviceTask(initial_device, message_handler,
                                          storage_pool_manager))
        
        self.addTask(query_device,
                     QueryDeviceTask(query_device, message_handler,
                                     storage_pool_manager))
        
        self.addTask(create_device,
                     CreateDeviceTask(create_device, message_handler,
                                      storage_pool_manager))
        
        self.addTask(modify_device,
                     ModifyDeviceTask(modify_device, message_handler,
                                      storage_pool_manager))
        
        self.addTask(delete_device,
                     DeleteDeviceTask(delete_device, message_handler,
                                      storage_pool_manager))
        
        #---------------------------

        ##compute pool
        self.addTask(query_compute_pool,
                     QueryComputePoolTask(query_compute_pool, message_handler, status_manager, compute_pool_manager))
        
        self.addTask(query_compute_pool_detail,
                     QueryComputePoolDetailTask(query_compute_pool_detail, message_handler, compute_pool_manager))
        
        self.addTask(create_compute_pool,
                     CreateComputePoolTask(create_compute_pool, message_handler,
                                          compute_pool_manager, address_manager, port_manager, storage_pool_manager))

        self.addTask(modify_compute_pool,
                     ModifyComputePoolTask(modify_compute_pool, message_handler, compute_pool_manager, address_manager, port_manager, storage_pool_manager, service_manager))
        
        self.addTask(delete_compute_pool,
                     DeleteComputePoolTask(delete_compute_pool, message_handler, compute_pool_manager, status_manager))
        
        self.addTask(add_compute_resource,
                     AddComputeResourceTask(add_compute_resource, message_handler,
                                          compute_pool_manager, service_manager))
        
        self.addTask(remove_compute_resource,
                     RemoveComputeResourceTask(remove_compute_resource, message_handler,
                                          compute_pool_manager))
        
        self.addTask(query_compute_resource,
                     QueryComputeResourceTask(query_compute_resource, message_handler,
                                              config_manager,
                                              status_manager,
                                              compute_pool_manager,
                                              service_manager))

        ##server room
        self.addTask(query_server_room,
                     QueryServerRoomTask(query_server_room, message_handler,
                                         status_manager,
                                         config_manager))

        self.addTask(create_server_room,
                     CreateServerRoomTask(create_server_room, message_handler,
                                         config_manager))

        self.addTask(delete_server_room,
                     DeleteServerRoomTask(delete_server_room, message_handler,
                                         config_manager))

        self.addTask(modify_server_room,
                     ModifyServerRoomTask(modify_server_room, message_handler,
                                         config_manager))

        ##server rack
        self.addTask(query_server_rack,
                     QueryServerRackTask(query_server_rack, message_handler,
                                         status_manager, config_manager))

        self.addTask(create_server_rack,
                     CreateServerRackTask(create_server_rack, message_handler,
                                         config_manager))

        self.addTask(delete_server_rack,
                     DeleteServerRackTask(delete_server_rack, message_handler,
                                         config_manager))

        self.addTask(modify_server_rack,
                     ModifyServerRackTask(modify_server_rack, message_handler,
                                         config_manager))

        ##server
        self.addTask(query_server,
                     QueryServerTask(query_server, message_handler,
                                     status_manager, config_manager))

        self.addTask(add_server,
                     AddServerTask(add_server, message_handler,
                                       config_manager))

        self.addTask(remove_server,
                     RemoveServerTask(remove_server, message_handler,
                                          config_manager))

        self.addTask(modify_server,
                     ModifyServerTask(modify_server, message_handler,
                                      config_manager))        
        ##service
        self.addTask(query_service_type,
                     QueryServiceTypeTask(query_service_type, message_handler,
                                     service_manager))

        self.addTask(query_service_group,
                     QueryServiceGroupTask(query_service_group, message_handler,
                                       service_manager))

        self.addTask(query_service,
                     QueryServiceTask(query_service, message_handler,
                                          service_manager))
        
        self.addTask(modify_service,
                     ModifyServiceTask(modify_service, message_handler, service_manager))
        
        self.addTask(synch_service_status,
                     SyncServiceStatusTask(synch_service_status, message_handler, service_manager))

        self.addTask(query_whisper,
                     QueryWhisperTask(query_whisper, message_handler,
                                          service_manager))

        ##host
        self.addTask(query_host,
                     QueryHostTask(query_host, message_handler,
                                   compute_pool_manager,
                                   status_manager,
                                   config_manager, service_manager))

        self.addTask(query_host_info,
                     QueryHostInfoTask(query_host_info, message_handler,
                                       config_manager))
        
        self.addTask(create_host,
                     CreateHostTask(create_host, message_handler,
                                    status_manager,
                                    config_manager,
                                    compute_pool_manager,
                                    image_manager,
                                    address_manager,
                                    port_manager,
                                    forwarder_manager))

        self.addTask(modify_host,
                     ModifyHostTask(modify_host, message_handler,
                                    config_manager,
                                    compute_pool_manager,
                                    port_manager,
                                    forwarder_manager))

        self.addTask(delete_host,
                     DeleteHostTask(delete_host, message_handler,
                                    config_manager,
                                    compute_pool_manager,
                                    address_manager,
                                    port_manager,
                                    forwarder_manager,
                                    network_manager))

        self.addTask(start_host,
                     StartHostTask(start_host, message_handler, config_manager, iso_manager, service_manager))
        self.addTask(stop_host,
                     StopHostTask(stop_host, message_handler,
                                    config_manager,
                                    compute_pool_manager))
        self.addTask(halt_host,
                     HaltHostTask(halt_host, message_handler,
                                    config_manager,
                                    compute_pool_manager))


        self.addTask(restart_host,
                     RestartHostTask(restart_host, message_handler, config_manager, iso_manager, service_manager))
        
        self.addTask(reset_host,
                     ResetHostTask(reset_host, message_handler, config_manager))

        self.addTask(flush_disk_image,
                     FlushDiskImageTask(flush_disk_image, message_handler, config_manager, image_manager))

        self.addTask(backup_host,
                     BackupHostTask(backup_host, message_handler, config_manager))

        self.addTask(resume_backup,
                     ResumeBackupTask(resume_backup, message_handler, config_manager))

        self.addTask(query_host_backup,
                     QueryHostBackupTask(query_host_backup, message_handler, config_manager))
        
        self.addTask(insert_media,
                     InsertMediaTask(insert_media, message_handler, config_manager, iso_manager, service_manager))
        
        self.addTask(change_media,
                     ChangeMediaTask(change_media, message_handler, config_manager, iso_manager, service_manager))
        
        self.addTask(eject_media,
                     EjectMediaTask(eject_media, message_handler,
                                    config_manager,
                                    compute_pool_manager,
                                    iso_manager))

        self.addTask(attach_disk,
                     AttachDiskTask(attach_disk, message_handler,
                                    config_manager))        

        self.addTask(detach_disk,
                     DetachDiskTask(detach_disk, message_handler,
                                    config_manager))        

        ##iso image
        self.addTask(query_iso_image,
                     QueryISOImageTask(query_iso_image, message_handler,
                                     iso_manager))        

        self.addTask(upload_iso_image,
                     UploadISOImageTask(upload_iso_image, message_handler, iso_manager))
        self.addTask(modify_iso_image,
                     ModifyISOImageTask(modify_iso_image, message_handler,
                                     iso_manager))
        self.addTask(delete_iso_image,
                     DeleteISOImageTask(delete_iso_image, message_handler,
                                     iso_manager))

        ##disk image
        self.addTask(query_disk_image,
                     QueryDiskImageTask(query_disk_image, message_handler,
                                        image_manager))        

        self.addTask(create_disk_image,
                     CreateDiskImageTask(create_disk_image, message_handler,
                                         config_manager, service_manager,
                                         image_manager))
        
        self.addTask(modify_disk_image,
                     ModifyDiskImageTask(modify_disk_image, message_handler,
                                         image_manager))
        self.addTask(delete_disk_image,
                     DeleteDiskImageTask(delete_disk_image, message_handler,
                                         image_manager))
        ##forwarder

        self.addTask(set_forwarder_status,
                     SetForwarderStatusTask(set_forwarder_status, message_handler,
                                            forwarder_manager))
        self.addTask(query_forwarder_summary,
                     QueryForwarderSummaryTask(query_forwarder_summary, message_handler,
                                               forwarder_manager))
        self.addTask(query_forwarder,
                     QueryForwarderTask(query_forwarder, message_handler,
                                        forwarder_manager))
        self.addTask(get_forwarder,
                     GetForwarderTask(get_forwarder, message_handler,
                                      forwarder_manager))
        self.addTask(add_forwarder,
                     AddForwarderTask(add_forwarder, message_handler,
                                 config_manager,
                                 compute_pool_manager,
                                 address_manager,
                                 port_manager,
                                 forwarder_manager))

        self.addTask(remove_forwarder,
                     RemoveForwarderTask(remove_forwarder, message_handler,
                                 config_manager,
                                 compute_pool_manager,
                                 address_manager,
                                 port_manager,
                                 forwarder_manager))
        ## network
        self.addTask(create_network,
                     CreateNetworkTask(create_network, message_handler, network_manager, address_manager))
        
        self.addTask(modify_network,
                     ModifyNetworkTask(modify_network, message_handler, network_manager, address_manager, config_manager, forwarder_manager))
        
        self.addTask(delete_network,
                     DeleteNetworkTask(delete_network, message_handler, network_manager, address_manager))
        
        self.addTask(query_network,
                     QueryNetworkTask(query_network, message_handler, network_manager))
        
        self.addTask(query_network_detail,
                     QueryNetworkDetailTask(query_network_detail, message_handler, network_manager))
        
        self.addTask(start_network,
                     StartNetworkTask(start_network, message_handler, network_manager, config_manager, forwarder_manager))
        
        self.addTask(stop_network,
                     StopNetworkTask(stop_network, message_handler, network_manager, config_manager, forwarder_manager))
        
        self.addTask(query_network_host,
                     QueryNetworkHostTask(query_network_host, message_handler, network_manager, config_manager))
        
        self.addTask(attach_host,
                     AttachHostTask(attach_host, message_handler, network_manager, config_manager, forwarder_manager, address_manager, port_manager))
        
        self.addTask(detach_host,
                     DetachHostTask(detach_host, message_handler, config_manager, compute_pool_manager, address_manager, port_manager, forwarder_manager, network_manager))
        
        self.addTask(network_attach_address,
                     NetworkAttachAddressTask(network_attach_address, message_handler, network_manager, address_manager))
        
        self.addTask(network_detach_address,
                     NetworkDetachAddressTask(network_detach_address, message_handler, network_manager, address_manager))
        
        self.addTask(network_bind_port,
                     NetworkBindPortTask(network_bind_port, message_handler, network_manager, config_manager, forwarder_manager))
        
        self.addTask(network_unbind_port,
                     NetworkUnbindPortTask(network_unbind_port, message_handler, network_manager, config_manager, forwarder_manager))
        
        
        
        
        ##config
        self.addTask(check_config,
                     CheckConfigTask(check_config, message_handler,
                                     forwarder_manager))

        self.addTask(start_observe,
                     StartObserveTask(start_observe, message_handler, status_manager, config_manager, service_manager))        
        
        # snapshot pool
        self.addTask(initial_snapshot_pool,
                     InitialSnapshotPoolTask(initial_snapshot_pool, message_handler, snapshot_pool_manager, self))
        
        self.addTask(query_snapshot_pool,
                     QuerySnapshotPoolTask(query_snapshot_pool, message_handler, snapshot_pool_manager))
        
        self.addTask(create_snapshot_pool,
                     CreateSnapshotPoolTask(create_snapshot_pool, message_handler, snapshot_pool_manager))
        
        self.addTask(modify_snapshot_pool,
                     ModifySnapshotPoolTask(modify_snapshot_pool, message_handler, snapshot_pool_manager))
        
        self.addTask(delete_snapshot_pool,
                     DeleteSnapshotPoolTask(delete_snapshot_pool, message_handler, snapshot_pool_manager))
        
        # snapshot node
        self.addTask(initial_snapshot_node,
                     InitialSnapshotNodeTask(initial_snapshot_node, message_handler, snapshot_pool_manager))
        
        self.addTask(add_snapshot_node,
                     AddSnapshotNodeTask(add_snapshot_node, message_handler, snapshot_pool_manager))
        
        self.addTask(remove_snapshot_node,
                     RemoveSnapshotNodeTask(remove_snapshot_node, message_handler, snapshot_pool_manager))
        
        self.addTask(query_snapshot_node,
                     QuerySnapshotNodeTask(query_snapshot_node, message_handler, snapshot_pool_manager))
        
        # snapshot
        self.addTask(query_snapshot,
                     QuerySnapshotTask(query_snapshot, message_handler, config_manager))
        
        self.addTask(create_snapshot,
                     CreateSnapshotTask(create_snapshot, message_handler, config_manager))
        
        self.addTask(delete_snapshot,
                     DeleteSnapshotTask(delete_snapshot, message_handler, config_manager))
        
        self.addTask(resume_snapshot,
                     ResumeSnapshotTask(resume_snapshot, message_handler, config_manager))
        
        self.addTask(add_rule,
                     AddRuleTask(add_rule, message_handler))
        
        self.addTask(remove_rule,
                     RemoveRuleTask(remove_rule, message_handler))
        
        self.addTask(query_rule,
                     QueryRuleTask(query_rule, message_handler))
        
        #statistic
        self.addTask(query_operate_detail,
                     QueryOperateDetailTask(query_operate_detail, message_handler, config_manager))
        
        self.addTask(query_operate_summary,
                     QueryOperateSummaryTask(query_operate_summary, message_handler, config_manager))
        
        self.addTask(query_service_detail,
                     QueryServiceDetailTask(query_service_detail, message_handler))
        
        self.addTask(query_service_summary,
                     QueryServiceSummaryTask(query_service_summary, message_handler))
        
        #storage device
        self.addTask(query_storage_device,
                     QueryStorageDeviceTask(query_storage_device, message_handler, service_manager))
        
        self.addTask(add_storage_device,
                     AddStorageDeviceTask(add_storage_device, message_handler, service_manager))
        
        self.addTask(remove_storage_device,
                     RemoveStorageDeviceTask(remove_storage_device, message_handler, service_manager))
        
        self.addTask(enable_storage_device,
                     EnableStorageDeviceTask(enable_storage_device, message_handler, service_manager))
        
        self.addTask(disable_storage_device,
                     DisableStorageDeviceTask(disable_storage_device, message_handler, service_manager))
        
        self.addTask(storage_server_sync,
                     StorageServerSyncTask(storage_server_sync, message_handler, service_manager))

    def createSession(self, session_id):
        """
        create session instance, override by inherited class if necessary
        """
        session = TaskSession(session_id)
        return session

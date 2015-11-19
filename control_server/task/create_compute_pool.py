#!/usr/bin/python
from compute_pool import *
from service.message_define import *
from transaction.base_task import *
import string

class CreateComputePoolTask(BaseTask):

    def __init__(self, task_type, messsage_handler, compute_pool_manager, address_manager, port_manager, storage_pool_manager):
        self.compute_pool_manager = compute_pool_manager
        self.address_manager = address_manager
        self.port_manager = port_manager
        self.storage_pool_manager = storage_pool_manager
        logger_name = "task.create_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.create_compute_pool, messsage_handler, logger_name)

    def invokeSession(self, session):
        self.info("[%08X] <create_compute_pool> receive request from '%s'" %
                  (session.session_id, session.request_module))
        request = session.initial_message

        name = request.getString(ParamKeyDefine.name)
        network_type = request.getUInt(ParamKeyDefine.network_type)
        network = request.getString(ParamKeyDefine.network)
        disk_type = request.getUInt(ParamKeyDefine.disk_type)
        disk_source = request.getString(ParamKeyDefine.disk_source)
        path = request.getString(ParamKeyDefine.path)
        crypt = request.getString(ParamKeyDefine.crypt)
        mode = request.getUIntArray(ParamKeyDefine.mode)

        high_available = HighAvaliableModeEnum.disabled
        if mode != None and len(mode) >= 1 and mode[0] > 0:
            high_available = HighAvaliableModeEnum.enabled

        auto_qos = AutoQOSModeEnum.disabled
        if mode != None and len(mode) >= 2 and mode[1] > 0:
            auto_qos = AutoQOSModeEnum.enabled

        thin_provisioning = ThinProvisioningModeEnum.disabled
        if mode != None and len(mode) >= 3 and mode[2] > 0:
            thin_provisioning = ThinProvisioningModeEnum.enabled

        backing_image = BackingImageModeEnum.disabled
        if mode != None and len(mode) >= 4 and mode[3] > 0:
            backing_image = BackingImageModeEnum.enabled

        if backing_image == BackingImageModeEnum.enabled:
            if thin_provisioning != ThinProvisioningModeEnum.enabled:
                self.error("[%08X] <create_compute_pool> fail, backing_image enabled, but thin_provisioning diabled" %
                           (session.session_id))
                self.taskFail(session)
                return
            
            if disk_type != ComputeStorageTypeEnum.nas:
                self.error("[%08X] <create_compute_pool> fail, backing_image enabled, but disk_type is not nas, disk_type: %s" %
                           (session.session_id, disk_type))
                self.taskFail(session)
                return

        config = ComputePool()
        config.name = name
        config.network_type = network_type
        config.disk_type = disk_type
        config.high_available = high_available
        config.auto_qos = auto_qos
        config.thin_provisioning = thin_provisioning
        config.backing_image = backing_image

        if network_type not in (ComputeNetworkTypeEnum.private,
                                        ComputeNetworkTypeEnum.monopoly,
                                        ComputeNetworkTypeEnum.share,
                                        ComputeNetworkTypeEnum.bridge):
            self.error("[%08X] <create_compute_pool> create fail, invalid network type '%s'" %
                       (session.session_id, network_type))
            self.taskFail(session)
            return

        if network_type == ComputeNetworkTypeEnum.monopoly:
            if not self.address_manager.containsPool(network):
                self.error("[%08X] <create_compute_pool> create fail, invalid address pool id '%s'" % (session.session_id, network))
                self.taskFail(session)
                return
            config.network = network

        elif network_type == ComputeNetworkTypeEnum.share:
            if not self.port_manager.containsPool(network):
                self.error("[%08X] <create_compute_pool> create fail, invalid port pool id '%s'" % (session.session_id, network))
                self.taskFail(session)
                return
            config.network = network

        else:  # private,bridge
            config.network = ""

        if disk_type not in (ComputeStorageTypeEnum.local,
                                    ComputeStorageTypeEnum.cloud,
                                    ComputeStorageTypeEnum.nas,
                                    ComputeStorageTypeEnum.ip_san):
            self.error("[%08X] <create_compute_pool> create fail, invalid disk type '%s'" %
                       (session.session_id, disk_type))
            self.taskFail(session)
            return

        if disk_type == ComputeStorageTypeEnum.cloud:
            if not self.storage_pool_manager.isStoragePoolUUIDExists(disk_source):
                self.error("[%08X] <create_compute_pool> create fail, invalid storage pool '%s'" %
                           (session.session_id, disk_source))
                self.taskFail(session)
                return
            config.disk_source = disk_source

        elif disk_type == ComputeStorageTypeEnum.nas:
            if len(string.strip(path)) == 0:
                self.error("[%08X] <create_compute_pool> fail, invail path '%s'" %
                           (session.session_id, path))
                self.taskFail(session)
                return

            if len(string.strip(crypt)) == 0:
                self.error("[%08X] <create_compute_pool> fail, invalid crypt '%s'" %
                           (session.session_id, crypt))
                self.taskFail(session)
                return
            config.path = path
            config.crypt = crypt
            config.disk_source = ""
        else:  # local, ip_san
            config.disk_source = ""
            config.path = ""
            config.crypt = ""

        if not self.compute_pool_manager.createPool(config):
            self.error("[%08X] <create_compute_pool> create fail, name '%s'" % (session.session_id, name))
            self.taskFail(session)
            return

        self.info("[%08X] <create_compute_pool> create success, pool '%s'('%s')" % (session.session_id, name, config.uuid))

        response = getResponse(RequestDefine.create_compute_pool)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.uuid, config.uuid)

        self.sendMessage(response, session.request_module)
        session.finish()


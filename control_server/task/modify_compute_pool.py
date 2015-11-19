#!/usr/bin/python
from compute_pool import *
from string import strip
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, EventDefine, ParamKeyDefine, \
    getResponse, getRequest
from transaction.state_define import state_initial, result_success, result_fail, \
    result_any
from transport.app_message import AppMessage
from common import dict_util

class ModifyComputePoolTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, messsage_handler, compute_pool_manager, address_manager, port_manager, storage_pool_manager, service_manager):
        self.compute_pool_manager = compute_pool_manager
        self.address_manager = address_manager
        self.port_manager = port_manager
        self.storage_pool_manager = storage_pool_manager
        self.service_manager = service_manager
        logger_name = "task.modify_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.modify_compute_pool, messsage_handler, logger_name)

        rollback_modify_service = 1
        self.addState(rollback_modify_service)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_success, self.onSuccess, state_initial)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_fail, self.onFail, rollback_modify_service)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout, rollback_modify_service)

        self.addTransferRule(rollback_modify_service, AppMessage.RESPONSE, RequestDefine.modify_service, result_success, self.onRollbackSuccess, rollback_modify_service)
        self.addTransferRule(rollback_modify_service, AppMessage.RESPONSE, RequestDefine.modify_service, result_fail, self.onRollbackFail, rollback_modify_service)
        self.addTransferRule(rollback_modify_service, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackTimeout, rollback_modify_service)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message

        pool_id = request.getString(ParamKeyDefine.uuid)
        name = request.getString(ParamKeyDefine.name)
        network_type = request.getUInt(ParamKeyDefine.network_type)
        network = request.getString(ParamKeyDefine.network)
        disk_type = request.getUInt(ParamKeyDefine.disk_type)
        disk_source = request.getString(ParamKeyDefine.disk_source)
        mode = request.getUIntArray(ParamKeyDefine.mode)
        option = request.getUInt(ParamKeyDefine.option)
        path = request.getString(ParamKeyDefine.path)
        crypt = request.getString(ParamKeyDefine.crypt)

        v_parameter = {}
        v_parameter["uuid"] = pool_id;
        v_parameter["name"] = name;
        v_parameter["network_type"] = network_type;
        v_parameter["network"] = network;
        v_parameter["disk_type"] = disk_type;
        v_parameter["disk_source"] = disk_source;
        v_parameter["mode"] = mode;
        v_parameter["option"] = option;
        v_parameter["path"] = path;
        v_parameter["crypt"] = crypt;

#         self.info("[%08X] <modify_compute_pool> receive request from '%s', pool id '%s', option '%d'" % (session.session_id, session.request_module, pool_id, option))

        self.info("[%08X] <modify_compute_pool> receive request from '%s', parameter: %s" % (session.session_id, session.request_module, dict_util.toDictionary(v_parameter)))

        if not self.compute_pool_manager.containsPool(pool_id):
            self.error("[%08X] <modify_compute_pool> fail, invalid id '%s'" % (session.session_id, pool_id))
            self.taskFail(session)
            return

        # #check host
        has_host = False
        compute_pool = self.compute_pool_manager.getPool(pool_id)
        for node_resource in compute_pool.resource.values():
            if 0 != len(node_resource.allocated):
                has_host = True
                break

        if option == 0:  # not allow modify in normal mode when having hosts
            # #check host
            if has_host == True:
                self.error("[%08X] <modify_compute_pool> fail in normal mode, resource '%s' in pool '%s' not empty" %
                           (session.session_id, node_resource.name, compute_pool.name))
                self.taskFail(session)
                return
        else:  # forced mode
            if has_host == True:
                if compute_pool.network_type != network_type:  # not allow to change network type when having hosts
                    self.error("[%08X] <modify_compute_pool> fail in forced mode, pool '%s'('%s'), which has hosts, is not allow to change network type" %
                               (session.session_id, compute_pool.name, compute_pool.uuid))
                    self.taskFail(session)
                    return

                if compute_pool.disk_type != disk_type:  # not allow to change disk type when having hosts
                    self.error("[%08X] <modify_compute_pool> fail in forced mode, pool '%s'('%s'), which has hosts, is not allow to change disk type" %
                               (session.session_id, compute_pool.name, compute_pool.uuid))
                    self.taskFail(session)
                    return

        # check network source
        if network_type not in (ComputeNetworkTypeEnum.private, ComputeNetworkTypeEnum.monopoly, ComputeNetworkTypeEnum.share, ComputeNetworkTypeEnum.bridge):
            self.error("[%08X] <modify_compute_pool> fail, network type '%d' not support" %
                       (session.session_id, network_type))
            self.taskFail(session)
            return

        if network_type == ComputeNetworkTypeEnum.monopoly:
            if not self.address_manager.containsPool(network):
                self.error("[%08X] <modify_compute_pool> fail, address pool '%s' does not exist" %
                           (session.session_id, network))
                self.taskFail(session)
                return

        elif network_type == ComputeNetworkTypeEnum.share:
            if not self.port_manager.containsPool(network):
                self.error("[%08X] <modify_compute_pool> fail, port pool '%s' does not exist" %
                           (session.session_id, network))
                self.taskFail(session)
                return

        else:  # private, bridge
            network = ""

        # check disk source
        if disk_type not in (ComputeStorageTypeEnum.local, ComputeStorageTypeEnum.cloud, ComputeStorageTypeEnum.nas, ComputeStorageTypeEnum.ip_san):
            self.error("[%08X] <modify_compute_pool> fail, disk type '%d' not support" %
                       (session.session_id, disk_type))
            self.taskFail(session)
            return

        if disk_type == ComputeStorageTypeEnum.cloud:
            if not self.storage_pool_manager.isStoragePoolUUIDExists(disk_source):
                self.error("[%08X] <modify_compute_pool> fail, storage pool '%s' does not exist" %
                           (session.session_id, disk_source))
                self.taskFail(session)
                return
            path = ""
            crypt = ""
        elif disk_type == ComputeStorageTypeEnum.nas:
            if 0 == len(strip(path)):
                self.error("[%08X] <modify_compute_pool> fail, invalid path '%s'" %
                           (session.session_id, path))
                self.taskFail(session)
                return

            if 0 == len(strip(crypt)):
                self.error("[%08X] <modify_compute_pool> fail, invalid crypt '%s'" %
                           (session.session_id, crypt))
                self.taskFail(session)
                return
            disk_source = ""
        else:  # local, ip_san
            disk_source = ""
            path = ""
            crypt = ""

        config = ComputePool()
        config.uuid = pool_id
        config.name = name
        config.status = compute_pool.status
        config.network_type = network_type
        config.network = network
        config.disk_type = disk_type
        config.disk_source = disk_source
        config.path = path
        config.crypt = crypt

        if mode != None and len(mode) >= 1:
            config.high_available = HighAvaliableModeEnum.enabled if mode[0] > 0 else HighAvaliableModeEnum.disabled
        else:
            config.high_available = compute_pool.high_available

        if mode != None and len(mode) >= 2:
            config.auto_qos = AutoQOSModeEnum.enabled if mode[1] > 0 else AutoQOSModeEnum.disabled
        else:
            config.auto_qos = compute_pool.auto_qos

        if mode != None and len(mode) >= 3:
            config.thin_provisioning = ThinProvisioningModeEnum.enabled if mode[2] > 0 else ThinProvisioningModeEnum.disabled
        else:
            config.thin_provisioning = compute_pool.thin_provisioning

        if mode != None and len(mode) >= 4:
            config.backing_image = BackingImageModeEnum.enabled if mode[3] > 0 else BackingImageModeEnum.disabled
        else:
            config.backing_image = compute_pool.backing_image

        if config.backing_image == BackingImageModeEnum.enabled:
            if config.thin_provisioning != ThinProvisioningModeEnum.enabled:
                self.error("[%08X] <modify_compute_pool> fail, backing_image enabled, but thin_provisioning diabled" % (session.session_id))
                self.taskFail(session)
                return

            if disk_type != ComputeStorageTypeEnum.nas:
                self.error("[%08X] <modify_compute_pool> fail, backing_image enabled, but disk_type is not nas, disk_type: %s" % (session.session_id, disk_type))
                self.taskFail(session)
                return

        if disk_type == compute_pool.disk_type:

            if not self.compute_pool_manager.modifyPool(pool_id, config):
                self.error("[%08X] <modify_compute_pool> fail, name '%s'" %
                           (session.session_id, config.name))
                self.taskFail(session)
                return

            self.info("[%08X] <modify_compute_pool> success, pool '%s'('%s'), address type %d/pool '%s', storage type %d/pool '%s', high available '%d', auto qos '%d'" %
                      (session.session_id, config.name, pool_id,
                       config.network_type, config.network,
                       config.disk_type, config.disk_source, config.high_available, config.auto_qos))

            response = getResponse(RequestDefine.modify_compute_pool)
            response.session = session.request_session
            response.success = True
            self.sendMessage(response, session.request_module)
            session.finish()

        else:

            self.info("[%08X] <modify_compute_pool> request modify service, disk type '%d'" %
                      (session.session_id, disk_type))

            target_list = []
            for resource in compute_pool.resource.keys():
                target_list.append(resource)

            session.target_list = target_list
            session.offset = -1
            session.config = config
            session.compute_pool = compute_pool

            self.startRequest(session)


    def startRequest(self, session):
        offset = session.offset + 1
        config = session.config

        if offset < len(session.target_list):

            node_client = session.target_list[offset]
            session.offset = offset

            modify_request = getRequest(RequestDefine.modify_service)
            modify_request.session = session.session_id
            modify_request.setUInt(ParamKeyDefine.disk_type, config.disk_type)
            modify_request.setString(ParamKeyDefine.disk_source, config.path)
            modify_request.setString(ParamKeyDefine.crypt, config.crypt)

            self.sendMessage(modify_request, node_client)
            self.info("[%08X] <modify_compute_pool> send modify_service request to '%s'" % (session.session_id, node_client))
            self.setTimer(session, self.timeout)

        else:

            # success
            if not self.compute_pool_manager.modifyPool(config.uuid, config):
                self.error("[%08X] <modify_compute_pool> fail, name '%s'" % (session.session_id, config.name))
                self.taskFail(session)
                return

            self.info("[%08X] <modify_compute_pool> success, pool '%s'('%s'), address type %d/pool '%s', storage type %d/pool '%s', high available '%d', auto qos '%d'" %
                      (session.session_id, config.name, config.uuid,
                       config.network_type, config.network,
                       config.disk_type, config.disk_source, config.high_available, config.auto_qos))

            response = getResponse(RequestDefine.modify_compute_pool)
            response.session = session.request_session
            response.success = True
            self.sendMessage(response, session.request_module)
            session.finish()


    def onSuccess(self, msg, session):
        self.clearTimer(session)
        target = session.target_list[session.offset]
        self.info("[%08X] <modify_compute_pool> modify service success, target '%s'" % (session.session_id, target))

        # # modify service cache
        service = self.service_manager.getService(target)
        config = session.config
        if service != None:
            service.disk_type = config.disk_type

        self.startRequest(session)


    def onFail(self, msg, session):
        self.clearTimer(session)
        target = session.target_list[session.offset]
        self.error("[%08X] <modify_compute_pool> modify service fail, target '%s'" % (session.session_id, target))

        self.info("[%08X] <modify_compute_pool> start to rollback..." % (session.session_id))
        session.offset += 1
        self.startRollback(session)


    def onTimeout(self, msg, session):
        target = session.target_list[session.offset]
        self.error("[%08X] <modify_compute_pool> modify service timeout, target '%s'" % (session.session_id, target))

        self.info("[%08X] <modify_compute_pool> start to rollback..." % (session.session_id))
        session.offset += 1
        self.startRollback(session)


    def startRollback(self, session):
        offset = session.offset - 1
        compute_pool = session.compute_pool

        if offset >= 0:
            node_client = session.target_list[offset]
            session.offset = offset

            modify_request = getRequest(RequestDefine.modify_service)
            modify_request.session = session.session_id
            modify_request.setUInt(ParamKeyDefine.disk_type, compute_pool.disk_type)
            modify_request.setString(ParamKeyDefine.disk_source, compute_pool.path)
            modify_request.setString(ParamKeyDefine.crypt, compute_pool.crypt)

            self.sendMessage(modify_request, node_client)
            self.setTimer(session, self.timeout)
        else:
            self.error("[%08X] <modify_compute_pool> fail" % (session.session_id))
            self.taskFail(session)


    def onRollbackSuccess(self, msg, session):
        self.clearTimer(session)
        target = session.target_list[session.offset]
        self.info("[%08X] <modify_compute_pool> rollback modify service success, target '%s'" % (session.session_id, target))

        # # modify service cache
        service = self.service_manager.getService(target)
        compute_pool = session.compute_pool
        if service != None:
            service.disk_type = compute_pool.disk_type

        self.startRollback(session)


    def onRollbackFail(self, msg, session):
        self.clearTimer(session)
        target = session.target_list[session.offset]
        self.warn("[%08X] <modify_compute_pool> rollback modify service fail, target '%s'" % (session.session_id, target))

        self.startRollback(session)


    def onRollbackTimeout(self, msg, session):
        target = session.target_list[session.offset]
        self.warn("[%08X] <modify_compute_pool> rollback modify service timeout, target '%s'" % (session.session_id, target))

        self.startRollback(session)


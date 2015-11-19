#!/usr/bin/python
from host_forwarder import ForwarderPort
from host_forwarder import ForwarderTypeEnum
from host_info import HostPort
from service.message_define import EventDefine
from service.message_define import RequestDefine, ParamKeyDefine, getResponse
from service.message_define import getRequest
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_initial
from transport.app_message import AppMessage

class ModifyNetworkMode(object):
    normal = 0
    forced = 1

class ModifyNetworkTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, messsage_handler, network_manager, address_manager, config_manager, forwarder_manager):
        self.network_manager = network_manager
        self.address_manager = address_manager
        self.config_manager = config_manager
        self.forwarder_manager = forwarder_manager
        logger_name = "task.modify_network"
        BaseTask.__init__(self, task_type, RequestDefine.modify_network, messsage_handler, logger_name)

        forward_unbind_port = 1
        forward_remove_forwarder = 2
        forward_bind_port = 3
        rollback_start = 4
        rollback_add_forwarder = 5
        rollback_bind_port = 6
        rollback_remove_forwarder = 7

        self.addState(forward_unbind_port)
        self.addState(forward_remove_forwarder)
        self.addState(forward_bind_port)
        self.addState(rollback_start)
        self.addState(rollback_add_forwarder)
        self.addState(rollback_bind_port)
        self.addState(rollback_remove_forwarder)

        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_success, self.onUnbindPortSuccess, forward_unbind_port)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_fail, self.onUnbindPortFail, rollback_remove_forwarder)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onUnbindPortTimeout, rollback_remove_forwarder)

        # forward_unbind_port
        self.addTransferRule(forward_unbind_port, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRemoveForwarderSuccess, forward_remove_forwarder)
        self.addTransferRule(forward_unbind_port, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail, self.onRemoveForwarderFail, rollback_bind_port)
        self.addTransferRule(forward_unbind_port, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRemoveForwarderTimeout, rollback_bind_port)

        # forward_remove_forwarder
        self.addTransferRule(forward_remove_forwarder, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_success, self.onBindPortSuccess, forward_bind_port)
        self.addTransferRule(forward_remove_forwarder, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_fail, self.onBindPortFail, rollback_add_forwarder)
        self.addTransferRule(forward_remove_forwarder, AppMessage.EVENT, EventDefine.timeout, result_any, self.onBindPortTimeout, rollback_add_forwarder)

        # forward_bind_port
        self.addTransferRule(forward_bind_port, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onAddForwarderSuccess, state_initial)
        self.addTransferRule(forward_bind_port, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail, self.onAddForwarderFail, rollback_start)
        self.addTransferRule(forward_bind_port, AppMessage.EVENT, EventDefine.timeout, result_any, self.onAddForwarderTimeout, rollback_start)

        # rollback_start
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRollbackAddForwarderSuccess, rollback_add_forwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail, self.onRollbackAddForwarderFail, rollback_add_forwarder)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackAddForwarderTimeout, rollback_add_forwarder)

        # rollback_start
        self.addTransferRule(rollback_start, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_success, self.onRollbackAddForwarderSuccess, rollback_add_forwarder)
        self.addTransferRule(rollback_start, AppMessage.RESPONSE, RequestDefine.remove_forwarder, result_fail, self.onRollbackAddForwarderFail, rollback_add_forwarder)
        self.addTransferRule(rollback_start, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackAddForwarderTimeout, rollback_add_forwarder)

        # rollback_add_forwarder
        self.addTransferRule(rollback_add_forwarder, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_success, self.onRollbackBindPortSuccess, rollback_bind_port)
        self.addTransferRule(rollback_add_forwarder, AppMessage.RESPONSE, RequestDefine.network_unbind_port, result_fail, self.onRollbackBindPortFail, rollback_bind_port)
        self.addTransferRule(rollback_add_forwarder, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackBindPortTimeout, rollback_bind_port)

        # rollback_bind_port
        self.addTransferRule(rollback_bind_port, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_success, self.onRollbackRemoveForwarderSuccess, rollback_remove_forwarder)
        self.addTransferRule(rollback_bind_port, AppMessage.RESPONSE, RequestDefine.add_forwarder, result_fail, self.onRollbackRemoveForwarderFail, rollback_remove_forwarder)
        self.addTransferRule(rollback_bind_port, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackRemoveForwarderTimeout, rollback_remove_forwarder)

        # rollback_remove_forwarder
        self.addTransferRule(rollback_remove_forwarder, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_success, self.onRollbackUnbindPortSuccess, rollback_start)
        self.addTransferRule(rollback_remove_forwarder, AppMessage.RESPONSE, RequestDefine.network_bind_port, result_fail, self.onRollbackUnbindPortFail, rollback_start)
        self.addTransferRule(rollback_remove_forwarder, AppMessage.EVENT, EventDefine.timeout, result_any, self.onRollbackUnbindPortTimeout, rollback_start)

    def invokeSession(self, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        name = request.getString(ParamKeyDefine.name)
        description = request.getString(ParamKeyDefine.description)
        pool = request.getString(ParamKeyDefine.pool)
        ip = request.getStringArrayArray(ParamKeyDefine.ip)
        option = request.getUInt(ParamKeyDefine.option)

        self.info("[%08X] receive modify network request from '%s', uuid '%s', name '%s', pool '%s', ip '%s', option '%d'" %
                  (session.session_id, session.request_module, uuid, name, pool, ip, option))

        if not self.network_manager.containsNetwork(uuid):
            self.error("[%08X] modify network fail, network '%s' does not exist" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        network_info = self.network_manager.getNetwork(uuid).copy()

        if option not in (ModifyNetworkMode.normal, ModifyNetworkMode.forced):
            self.error("[%08X] modify network fail, option '%d' not support" %
                       (session.session_id, option))
            self.taskFail(session)
            return

        if option == ModifyNetworkMode.normal:
            if len(pool) != 0:
                self.error("[%08X] modify network fail in normal mode, pool should be empty or change the pool in forced mode" %
                           (session.session_id))
                self.taskFail(session)
                return

            if bool(ip) == True:
                self.error("[%08X] modify network fail in normal mode, ip should be empty or change the ip in forced mode" %
                           (session.session_id))
                self.taskFail(session)
                return

            network_info.name = name
            network_info.description = description
            if not self.network_manager.putNetwork(network_info):
                self.error("[%08X] modify network fail in normal mode, uuid '%s', name '%s'" %
                           (session.session_id, uuid, name))
                self.taskFail(session)
                return

            self.info("[%08X] modify network success in normal mode, uuid '%s', name '%s'" %
                      (session.session_id, network_info.uuid, network_info.name))
            response = getResponse(RequestDefine.modify_network)
            response.session = session.request_session
            response.success = True
            self.sendMessage(response, session.request_module)
            session.finish()
        elif option == ModifyNetworkMode.forced:
            if not self.address_manager.containsPool(pool):
                self.error("[%08X] modify network fail in forced mode, address pool '%s' does not exist" %
                           (session.session_id, pool))
                self.taskFail(session)
                return
            address_pool = self.address_manager.getPool(pool)

            intelligent_router = self.message_handler.getDefaultIntelligentRouter()
            if intelligent_router == None:
                self.error("[%08X] modify network fail in forced mode, no active intelligent router" %
                           session.session_id)
                self.taskFail(session)
                return

            if pool == network_info.pool:
                self.error("[%08X] modify network fail in forced mode, address pool '%s' should not be same with original one" %
                           (session.session_id, pool))
                self.taskFail(session)
                return

            old_ip_list = []
            new_ip_list = []
            if ip != None:
                for ip_tuple in ip:
                    if len(ip_tuple) != 2:
                        self.error("[%08X] modify network fail in forced mode, invalid parameter ip '%s', it should be in format [[old_ip, new_ip], ...]" %
                                   (session.session_id, ip))
                        self.taskFail(session)
                        return
                    old_ip, new_ip = ip_tuple[0], ip_tuple[1]
                    if not network_info.containsPublicIp(old_ip):
                        self.error("[%08X] modify network fail in forced mode, network '%s'('%s') does not contain public ip '%s'" %
                                   (session.session_id, network_info.name, network_info.uuid, old_ip))
                        self.taskFail(session)
                        return

                    if not address_pool.isAvailableIp(new_ip):
                        self.error("[%08X] modify network fail in forced mode, ip '%s' in address pool '%s'('%s') is not available" %
                                   (session.session_id, new_ip, address_pool.name, address_pool.uuid))
                        self.taskFail(session)
                        return

                    old_ip_list.append(old_ip)
                    new_ip_list.append(new_ip)

            # allocated specify ip
            for new_ip in new_ip_list:
                address_pool.setAllocated(new_ip)

            # construct old_ip_list and new_ip_list
            for old_ip in network_info.public_ips:
                if old_ip not in old_ip_list:
                    old_ip_list.append(old_ip)
                    new_ip = address_pool.allocate()
                    if new_ip == None:
                        self.error("[%08X] modify network fail in forced mode, address pool '%s'('%s') does not have enough ips" %
                                   (session.session_id, address_pool.name, address_pool.uuid))
                        # deallocate all new ip
                        self.deallocateIp(address_pool.uuid, new_ip_list)
                        self.taskFail(session)
                        return
                    new_ip_list.append(new_ip)

            # construct bound_port_map
            # format : {host_uuid:[(protocol, public_ip, public_port, host_port), ...]}
            bound_port_map = {}
            host_list = []
            for key, value in network_info.bound_ports.items():
                key_array = key.split(":")
                value_array = value.split(":")
                protocol = int(key_array[0])
                public_ip = key_array[1]
                public_port = int(key_array[2])
                host_uuid = value_array[0]
                host_port = int(value_array[1])

                if not bound_port_map.has_key(host_uuid):
                    bound_port_info = []
                    bound_port_map[host_uuid] = bound_port_info
                else:
                    bound_port_info = bound_port_map[host_uuid]

                bound_port_info.append((protocol, public_ip, public_port, host_port))
                host_list.append(host_uuid)

            # all self defined field in session
            session.intelligent_router = intelligent_router
            session.old_ip_list = old_ip_list  # [old_ip1, old_ip2, ...]
            session.new_ip_list = new_ip_list  # [new_ip1, new_ip2, ...]
            session.host_list = host_list  # [host_uuid1, host_uuid2, ...]
            session.success_host_list = []  # [success_host_uuid1, success_host_uuid2, ...]
            session.bound_port_map = bound_port_map  # {host_uuid:[(protocol, public_ip, public_port, host_port), ...]}
            session.target_host = None  # HostInfo object
            session.target_forwarder = None  # HostForwarder object

            self.startHostMigration(session)

    # network_unbind_port request
    def startHostMigration(self, session):
        host_list = session.host_list
        bound_port_map = session.bound_port_map

        # termination condition
        if len(host_list) == 0:
            self.success(session)
            return

        # target_host
        host_uuid = host_list.pop(0)
        if not self.config_manager.containsHost(host_uuid):
            self.error("[%08X] <modify_network> host '%s' does not exist, begin to rollback" %
                       (session.session_id, host_uuid))
            # rollback
            self.startHostRollback(session)
            return
        target_host = self.config_manager.getHost(host_uuid)

        # target_forwarder
        forwarder_uuid = target_host.forwarder
        if not self.forwarder_manager.contains(forwarder_uuid):
            self.error("[%08X] <modify_network>forwarder '%s' of host '%s'('%s') does not exist, begin to rollback" %
                       (session.session_id, forwarder_uuid, target_host.name, target_host.uuid))
            # rollback
            self.startHostRollback(session)
            return
        target_forwarder = self.forwarder_manager.get(forwarder_uuid, copy=True)

        session.target_host = target_host
        session.target_forwarder = target_forwarder

        # construct unbind_port_list
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        unbind_port_list = []  # format : [protocol1, public_ip1, public_port1, host_port1, protocol2 ...]
        for protocol, public_ip, public_port, host_port in host_bound_port:
            unbind_port_list.append(str(protocol))
            unbind_port_list.append(public_ip)
            unbind_port_list.append(str(public_port))
            unbind_port_list.append(str(host_port))

        # network_unbind_port request
        unbind_port_request = getRequest(RequestDefine.network_unbind_port)
        unbind_port_request.session = session.session_id
        unbind_port_request.setString(ParamKeyDefine.uuid, target_host.uuid)
        unbind_port_request.setStringArray(ParamKeyDefine.port, unbind_port_list)
        self.sendMessage(unbind_port_request, target_host.container)

        self.setTimer(session, self.timeout)

    def onUnbindPortSuccess(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        bound_port_map = session.bound_port_map
        intelligent_router = session.intelligent_router

        self.info("[%08X] <modify_network> unbind host port(s) success, host '%s'('%s')" %
                  (session.session_id, target_host.name, target_host.uuid))
        # remove host_info port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, public_ip, public_port, host_port in host_bound_port:
            self.deleteHostPort(target_host, protocol, public_ip, public_port, host_port)

        # remove forward request
        remove_forwarder_request = getRequest(RequestDefine.remove_forwarder)
        remove_forwarder_request.session = session.session_id
        remove_forwarder_request.setString(ParamKeyDefine.uuid, target_forwarder.uuid)
        self.sendMessage(remove_forwarder_request, intelligent_router)

        self.setTimer(session, self.timeout)

    def onUnbindPortFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.error("[%08X] <modify_network> unbind port fail, host '%s'('%s'), begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid))

        # begin to rollback at unbind_port
        self.rollbackUnbindPort(session)

    def onUnbindPortTimeout(self, msg, session):
        target_host = session.target_host
        self.error("[%08X] <modify_network> unbind port timeout, host '%s'('%s'), begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid))

        # begin to rollback at unbind_port
        self.rollbackUnbindPort(session)

    def onRemoveForwarderSuccess(self, msg, session):
        self.clearTimer(session)
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list

        self.info("[%08X] <modify_network> remove forwarder success, forwarder id '%s', host '%s'('%s')" %
                  (session.session_id, target_forwarder.uuid, target_host.name, target_host.uuid))

        # remove forwarder port
        # construct bind_port_list
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        bind_port_list = []
        for protocol, old_ip, public_port, host_port in host_bound_port:
            self.deleteForwarderPort(target_forwarder, protocol, old_ip, public_port, host_port)
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            bind_port_list.append(str(protocol))
            bind_port_list.append(new_ip)
            bind_port_list.append(str(public_port))
            bind_port_list.append(str(host_port))
        self.forwarder_manager.put(target_forwarder)

        bind_port_request = getRequest(RequestDefine.network_bind_port)
        bind_port_request.session = session.session_id
        bind_port_request.setString(ParamKeyDefine.uuid, target_host.uuid)
        bind_port_request.setStringArray(ParamKeyDefine.port, bind_port_list)
        self.sendMessage(bind_port_request, target_host.container)

        self.setTimer(session, self.timeout)

    def onRemoveForwarderFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.error("[%08X] <modify_network> remove forwarder fail, host '%s'('%s') remove forward '%s' fail, begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid, target_forwarder.uuid))

        # begin to rollback at remove_forwarder
        self.rollbackRemoveForwarder(session)

    def onRemoveForwarderTimeout(self, msg, session):
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.error("[%08X] <modify_network> remove forwarder timeout, host '%s'('%s') remove forward %s' timeout" %
                   (session.session_id, target_host.name, target_host.uuid, target_forwarder.uuid))

        # begin to rollback at remove_forwarder
        self.rollbackRemoveForwarder(session)

    def onBindPortSuccess(self, msg, session):
        self.clearTimer(session)
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list
        intelligent_router = session.intelligent_router

        self.info("[%08X] <modify_network> bind port(s) success, host '%s'('%s')" %
                  (session.session_id, target_host.name, target_host.uuid))
        # add host port
        # construct ip_list and forward
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        public_ip_list = []  # format : [public_ip1, public_ip2, ...]
        forward = []  # format : [protocol1, public_ip1_index, public_port1, host_port1, protocol2, ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            self.addHostPort(target_host, protocol, new_ip, public_port, host_port)
            # add new_ip into public_ip_list, and not allow repeat
            if new_ip not in public_ip_list:
                public_ip_list.append(new_ip)
            new_ip_index = public_ip_list.index(new_ip)
            forward.append(int(protocol))
            forward.append(new_ip_index)
            forward.append(int(public_port))
            forward.append(int(host_port))

        ip_list = [target_forwarder.server_ip]  # format : [server_ip, public_ip1, public_ip2, ...]
        ip_list.extend(public_ip_list)

        address = ""
        netmask = ""
        if bool(target_forwarder.vpc_range):
            address, netmask = target_forwarder.vpc_range.split("/")

        add_forwarder_request = getRequest(RequestDefine.add_forwarder)
        add_forwarder_request.session = session.session_id
        add_forwarder_request.setString(ParamKeyDefine.uuid, target_forwarder.uuid)
        add_forwarder_request.setUInt(ParamKeyDefine.type, ForwarderTypeEnum.vpc)
        add_forwarder_request.setString(ParamKeyDefine.host, target_forwarder.host_id)
        add_forwarder_request.setString(ParamKeyDefine.name, target_forwarder.host_name)
        add_forwarder_request.setStringArray(ParamKeyDefine.ip, ip_list)
        add_forwarder_request.setUIntArray(ParamKeyDefine.display_port, [target_forwarder.server_monitor, target_forwarder.public_monitor])
        add_forwarder_request.setUIntArray(ParamKeyDefine.port, [])
        add_forwarder_request.setString(ParamKeyDefine.network_address, target_forwarder.vpc_ip)
        add_forwarder_request.setString(ParamKeyDefine.address, address)
        add_forwarder_request.setUInt(ParamKeyDefine.netmask, int(netmask))
        add_forwarder_request.setUIntArray(ParamKeyDefine.forward, forward)
        add_forwarder_request.setUIntArray(ParamKeyDefine.range, target_forwarder.output_port_range)
        add_forwarder_request.setUInt(ParamKeyDefine.status, int(target_forwarder.enable))
        self.sendMessage(add_forwarder_request, intelligent_router)

        self.setTimer(session, self.timeout)

    def onBindPortFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.error("[%08X] <modify_network> bind port fail, host '%s'('%s'), begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid))

        # begin to rollback at bind_port
        self.rollbackBindPort(session)

    def onBindPortTimeout(self, msg, session):
        target_host = session.target_host
        self.error("[%08X] <modify_network> bind port timeout, host '%s'('%s'), begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid))

        # begin to rollback at bind_port
        self.rollbackBindPort(session)

    def onAddForwarderSuccess(self, msg, session):
        self.clearTimer(session)
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list
        success_host_list = session.success_host_list

        self.info("[%08X] <modify_network> add forwarder success, forwarder id '%s', host '%s'('%s')" %
                  (session.session_id, target_forwarder.uuid, target_host.name, target_host.uuid))
        # add forwarder port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            self.addForwarderPort(target_forwarder, protocol, new_ip, public_port, host_port)
        self.forwarder_manager.put(target_forwarder)

        self.info("[%08X] <modify_network> host '%s'('%s') public ip(s) migration finish" %
                  (session.session_id, target_host.name, target_host.uuid))
        success_host_list.append(target_host.uuid)
        session.target_host = None  # HostInfo object
        session.target_forwarder = None  # HostForwarder object
        self.startHostMigration(session)

    def onAddForwarderFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.warn("[%08X] <modify_network> add forwarder fail, host '%s'('%s'), forwarder id '%s', begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid, target_forwarder.uuid))
        # roll back beginning at add_forwarder
        self.rollbackAddForwarder(session)

    def onAddForwarderTimeout(self, msg, session):
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.warn("[%08X] <modify_network> add forwarder timeout, host '%s'('%s'), forwarder id '%s', begin to rollback" %
                   (session.session_id, target_host.name, target_host.uuid, target_forwarder.uuid))
        # roll back beginning at add_forwarder
        self.rollbackAddForwarder(session)

    def rollbackAddForwarder(self, session):
        target_forwarder = session.target_forwarder
        intelligent_router = session.intelligent_router

        remove_forwarder_request = getRequest(RequestDefine.remove_forwarder)
        remove_forwarder_request.session = session.session_id
        remove_forwarder_request.setString(ParamKeyDefine.uuid, target_forwarder.uuid)
        self.sendMessage(remove_forwarder_request, intelligent_router)

        self.setTimer(session, self.timeout)

    def onRollbackAddForwarderSuccess(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback add forwarder success, remove forwarder '%s' of host '%s'('%s')" %
                  (session.session_id, target_forwarder.uuid, target_host.name, target_host.uuid))

        self.rollbackAddForwarderCache(session)
        self.rollbackBindPort(session)

    def onRollbackAddForwarderFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback add forwarder fail, remove forwarder '%s' of host '%s'('%s') fail" %
                  (session.session_id, target_forwarder.uuid, target_host.name, target_host.uuid))

        self.rollbackAddForwarderCache(session)
        self.rollbackBindPort(session)

    def onRollbackAddForwarderTimeout(self, msg, session):
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback add forwarder timeout, remove forwarder '%s' of host '%s'('%s') timeout" %
                  (session.session_id, target_forwarder.uuid, target_host.name, target_host.uuid))

        self.rollbackAddForwarderCache(session)
        self.rollbackBindPort(session)

    def rollbackAddForwarderCache(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list

        # remove forwarder port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            self.deleteForwarderPort(target_forwarder, protocol, new_ip, public_port, host_port)
        self.forwarder_manager.put(target_forwarder)

    def rollbackBindPort(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list

        # construct unbind_port_list
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        unbind_port_list = []
        for protocol, old_ip, public_port, host_port in host_bound_port:
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            unbind_port_list.append(str(protocol))
            unbind_port_list.append(new_ip)
            unbind_port_list.append(str(public_port))
            unbind_port_list.append(str(host_port))

        unbind_port_request = getRequest(RequestDefine.network_unbind_port)
        unbind_port_request.session = session.session_id
        unbind_port_request.setString(ParamKeyDefine.uuid, target_host.uuid)
        unbind_port_request.setStringArray(ParamKeyDefine.port, unbind_port_list)
        self.sendMessage(unbind_port_request, target_host.container)

        self.setTimer(session, self.timeout)

    def onRollbackBindPortSuccess(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback bind port success, host '%s'('%s') unbind port(s) success" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.rollbackBindPortCache(session)
        self.rollbackRemoveForwarder(session)

    def onRollbackBindPortFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback bind port fail, host '%s'('%s') unbind port(s) fail" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.rollbackBindPortCache(session)
        self.rollbackRemoveForwarder(session)

    def onRollbackBindPortTimeout(self, msg, session):
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback bind port timeout, host '%s'('%s') unbind port(s) timeout" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.rollbackBindPortCache(session)
        self.rollbackRemoveForwarder(session)

    def rollbackBindPortCache(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list

        # remove host port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            index = old_ip_list.index(old_ip)
            new_ip = new_ip_list[index]
            self.deleteHostPort(target_host, protocol, new_ip, public_port, host_port)

    def rollbackRemoveForwarder(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder
        intelligent_router = session.intelligent_router

        # construct publci_ip_list and forward
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        public_ip_list = []
        forward = []
        for protocol, old_ip, public_port, host_port in host_bound_port:
            if old_ip not in public_ip_list:
                public_ip_list.append(old_ip)
            old_ip_index = public_ip_list.index(old_ip)
            forward.append(int(protocol))
            forward.append(old_ip_index)
            forward.append(int(public_port))
            forward.append(int(host_port))

        # add forwarder
        ip_list = [target_forwarder.server_ip]  # format : [server_ip, public_ip1, public_ip2, ...]
        ip_list.extend(public_ip_list)

        address = ""
        netmask = ""
        if bool(target_forwarder.vpc_range):
            address, netmask = target_forwarder.vpc_range.split("/")

        add_forwarder_request = getRequest(RequestDefine.add_forwarder)
        add_forwarder_request.session = session.session_id
        add_forwarder_request.setString(ParamKeyDefine.uuid, target_forwarder.uuid)
        add_forwarder_request.setUInt(ParamKeyDefine.type, ForwarderTypeEnum.vpc)
        add_forwarder_request.setString(ParamKeyDefine.host, target_forwarder.host_id)
        add_forwarder_request.setString(ParamKeyDefine.name, target_forwarder.host_name)
        add_forwarder_request.setStringArray(ParamKeyDefine.ip, ip_list)
        add_forwarder_request.setUIntArray(ParamKeyDefine.display_port, [target_forwarder.server_monitor, target_forwarder.public_monitor])
        add_forwarder_request.setUIntArray(ParamKeyDefine.port, [])
        add_forwarder_request.setString(ParamKeyDefine.network_address, target_forwarder.vpc_ip)
        add_forwarder_request.setString(ParamKeyDefine.address, address)
        add_forwarder_request.setUInt(ParamKeyDefine.netmask, int(netmask))
        add_forwarder_request.setUIntArray(ParamKeyDefine.forward, forward)
        add_forwarder_request.setUIntArray(ParamKeyDefine.range, target_forwarder.output_port_range)
        add_forwarder_request.setUInt(ParamKeyDefine.status, int(target_forwarder.enable))
        self.sendMessage(add_forwarder_request, intelligent_router)

        self.setTimer(session, self.timeout)

    def onRollbackRemoveForwarderSuccess(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forworder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback remove forwarder success, host '%s'('%s') add forwarder '%s'" %
                  (session.session_id, target_host.name, target_host.uuid, target_forworder.uuid))

        self.rollbackRemoveForwarderCache(session)
        self.rollbackUnbindPort(session)

    def onRollbackRemoveForwarderFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        target_forworder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback remove forwarder fail, host '%s'('%s') add forwarder '%s' fail" %
                  (session.session_id, target_host.name, target_host.uuid, target_forworder.uuid))

        self.rollbackRemoveForwarderCache(session)
        self.rollbackUnbindPort(session)

    def onRollbackRemoveForwarderTimeout(self, msg, session):
        target_host = session.target_host
        target_forworder = session.target_forwarder
        self.warn("[%08X] <modify_network> rollback remove forwarder timeout, host '%s'('%s') add forwarder '%s' timeout" %
                  (session.session_id, target_host.name, target_host.uuid, target_forworder.uuid))

        self.rollbackRemoveForwarderCache(session)
        self.rollbackUnbindPort(session)

    def rollbackRemoveForwarderCache(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        target_forwarder = session.target_forwarder

        # add forwarder port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            self.addForwarderPort(target_forwarder, protocol, old_ip, public_port, host_port)
        self.forwarder_manager.put(target_forwarder)

    def rollbackUnbindPort(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host

        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        bind_port_list = []
        for protocol, old_ip, public_port, host_port in host_bound_port:
            bind_port_list.append(str(protocol))
            bind_port_list.append(old_ip)
            bind_port_list.append(str(public_port))
            bind_port_list.append(str(host_port))

        bind_port_request = getRequest(RequestDefine.network_bind_port)
        bind_port_request.session = session.session_id
        bind_port_request.setString(ParamKeyDefine.uuid, target_host.uuid)
        bind_port_request.setStringArray(ParamKeyDefine.port, bind_port_list)
        self.sendMessage(bind_port_request, target_host.container)

        self.setTimer(session, self.timeout)

    def onRollbackUnbindPortSuccess(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback unbind port success, host '%s'('%s') bind port(s) success" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.finishHostRollback(session)

    def onRollbackUnbindPortFail(self, msg, session):
        self.clearTimer(session)
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback unbind port fail, host '%s'('%s') bind port(s) fail" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.finishHostRollback(session)

    def onRollbackUnbindPortTimeout(self, msg, session):
        target_host = session.target_host
        self.warn("[%08X] <modify_network> rollback unbind port timeout, host '%s'('%s') bind port(s) timeout" %
                  (session.session_id, target_host.name, target_host.uuid))

        self.finishHostRollback(session)

    def finishHostRollback(self, session):
        bound_port_map = session.bound_port_map
        target_host = session.target_host
        success_host_list = session.success_host_list
        # add host port
        host_bound_port = bound_port_map[target_host.uuid]  # format : [(protocol, public_ip, public_port, host_port), ...]
        for protocol, old_ip, public_port, host_port in host_bound_port:
            self.addHostPort(target_host, protocol, old_ip, public_port, host_port)

        if target_host.uuid in success_host_list:
            success_host_list.remove(target_host.uuid)

        self.info("[%08X] <modify_network> host '%s'('%s') rollback finish" %
                  (session.session_id, target_host.name, target_host.uuid))
        session.target_host = None
        session.target_forwarder = None
        self.startHostRollback(session)

    def startHostRollback(self, session):
        success_host_list = session.success_host_list

        while(True):
            # termination condition
            if len(success_host_list) == 0:
                self.fail(session)
                return

            # target_host
            host_uuid = success_host_list.pop()
            if not self.config_manager.containsHost(host_uuid):
                self.error("[%08X] <modify_network>rollback host fail and ignore it, host '%s' does not exist" %
                           (session.session_id, host_uuid))
                continue
            target_host = self.config_manager.getHost(host_uuid)

            # target_forwarder
            forwarder_uuid = target_host.forwarder
            if not self.forwarder_manager.contains(forwarder_uuid):
                self.error("[%08X] <modify_network>rollback host fail and ignore it, forwarder '%s' of host '%s'('%s') does not exist" %
                           (session.session_id, forwarder_uuid, target_host.name, target_host.uuid))
                continue
            target_forwarder = self.forwarder_manager.get(forwarder_uuid, copy=True)

            session.target_host = target_host
            session.target_forwarder = target_forwarder

            break

        self.rollbackAddForwarder(session)

    def deleteHostPort(self, host, protocol, public_ip, public_port, host_port):
        if not bool(host.port):
            return

        host_port_list = host.port[:]
        for port in host_port_list:
            if (int(port.protocol) == int(protocol)) and (port.public_ip == public_ip) and (int(port.public_port) == int(public_port)) and (int(port.host_port) == int(host_port)):
                host.port.remove(port)

    def addHostPort(self, host, protocol, public_ip, public_port, host_port):
        if host.port == None:
            host.port = []

        for port in host.port:
            if (int(port.protocol) == int(protocol)) and (port.public_ip == public_ip) and (int(port.public_port) == int(public_port)) and (int(port.host_port) == int(host_port)):
                return

        host_port_info = HostPort()
        host_port_info.protocol = int(protocol)
        host_port_info.public_ip = public_ip
        host_port_info.public_port = int(public_port)
        host_port_info.host_port = int(host_port)
        host.port.append(host_port_info)

    def deleteForwarderPort(self, forwarder, protocol, public_ip, public_port, host_port):
        if not bool(forwarder.port):
            return

        forwarder_port_list = forwarder.port[:]
        for port in forwarder_port_list:
            if (int(port.protocol) == int(protocol)) and (port.public_ip == public_ip) and (int(port.public_port) == int(public_port)) and (int(port.host_port) == int(host_port)):
                forwarder.port.remove(port)

    def addForwarderPort(self, forwarder, protocol, public_ip, public_port, host_port):
        if forwarder.port == None:
            forwarder.port = []

        for port in forwarder.port:
            if (int(port.protocol) == int(protocol)) and (port.public_ip == public_ip) and (int(port.public_port) == int(public_port)) and (int(port.host_port) == int(host_port)):
                return

        forwarder_port = ForwarderPort()
        forwarder_port.protocol = int(protocol)
        forwarder_port.public_ip = public_ip
        forwarder_port.public_port = int(public_port)
        forwarder_port.host_port = int(host_port)
        forwarder.port.append(forwarder_port)

    # deallocate ip
    def deallocateIp(self, pool, ip_list):
        address_pool = self.address_manager.getPool(pool)
        for ip in ip_list:
            address_pool.deallocate(ip)

    def fail(self, session):
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        pool = request.getString(ParamKeyDefine.pool)

        # deallocate old ip
        self.deallocateIp(pool, new_ip_list)

        network_info = self.network_manager.getNetwork(uuid)
        address_pool = self.address_manager.getPool(pool)
        self.error("[%08X] modify network fail in forced mode, network '%s'('%s'), pool '%s'('%s'), old ip list '%s', new ip list '%s'" %
                   (session.session_id, network_info.name, network_info.uuid, address_pool.name, address_pool.uuid, old_ip_list, new_ip_list))
        self.taskFail(session)

    def success(self, session):
        old_ip_list = session.old_ip_list
        new_ip_list = session.new_ip_list
        bound_port_map = session.bound_port_map

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        name = request.getString(ParamKeyDefine.name)
        description = request.getString(ParamKeyDefine.description)
        pool = request.getString(ParamKeyDefine.pool)

        network_info = self.network_manager.getNetwork(uuid).copy()

        # deallocate old ip
        self.deallocateIp(network_info.pool, old_ip_list)

        network_info.name = name
        network_info.description = description
        network_info.pool = pool

        # reset public ips
        network_info.public_ips.clear()
        for new_ip in new_ip_list:
            network_info.public_ips.add(new_ip)

        # reset bound ports
        bound_ports = network_info.bound_ports  # format : {host_uuid: [(protocol, public_ip, public_port, host_port), ...]}
        bound_ports.clear()
        for host_uuid, port_info_list in bound_port_map.items():
            for protocol, old_ip, public_port, host_port in port_info_list:
                old_ip_index = old_ip_list.index(old_ip)
                new_ip = new_ip_list[old_ip_index]
                key = "%s:%s:%s" % (protocol, new_ip, public_port)
                value = "%s:%s" % (host_uuid, host_port)
                bound_ports[key] = value

        self.network_manager.putNetwork(network_info)

        address_pool = self.address_manager.getPool(network_info.pool)
        self.info("[%08X] modify network success in forced mode, network '%s'('%s'), pool '%s'('%s'), old ip list '%s', new ip list '%s'" %
                  (session.session_id, network_info.name, network_info.uuid, address_pool.name, address_pool.uuid, old_ip_list, new_ip_list))

        response = getResponse(RequestDefine.modify_network)
        response.session = session.request_session
        response.success = True
        self.sendMessage(response, session.request_module)
        session.finish()


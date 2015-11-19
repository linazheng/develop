#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from compute_resource import *
from host_status import *

class QueryHostTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 compute_manager, status_manager, config_manager, service_manager):
        self.status_manager = status_manager
        self.compute_manager = compute_manager
        self.config_manager = config_manager
        self.service_manager = service_manager
        logger_name = "task.query_host"
        BaseTask.__init__(self, task_type, RequestDefine.query_host,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        target_range = request.getUInt(ParamKeyDefine.range)
        target = request.getString(ParamKeyDefine.target)

        host_in_node = []  # # [(host_id, node_client), ...]
        if target_range == 0:  # # query host in compute pool
            # compatible with the older interface
            if len(target) == 0:
                target = pool

            if not self.compute_manager.containsPool(target):
                self.error("[%08X] <query_host> fail, invalid compute pool id '%s'" %
                           (session.session_id, target))
                self.taskFail(session)
                return

            resource_list = self.compute_manager.queryResource(target)
            for resource in resource_list:
                for host_id in resource.allocated:
                    host_in_node.append((host_id, resource.name))

            self.info("[%08X] <query_host> success, %d host(s) in compute pool '%s'" %
                      (session.session_id, len(host_in_node), target))

        elif target_range == 1:  # # query host in the server
            if not self.config_manager.containsServer(target):
                self.error("[%08X] <query_host> fail, invalid server id '%s'" %
                           (session.session_id, target))
                self.taskFail(session)
                return

            service_list = self.service_manager.queryServicesInServer(target)
            node_client = None
            for service_name in service_list:
                service = self.service_manager.getService(service_name)
                if service.type == NodeTypeDefine.node_client:
                    node_client = service_name
                    break

            if node_client == None:
                self.warn("[%08X] <query_host> server '%s' is not a compute node" %
                          (session.session_id, target))
            else:
                contains, pool_id = self.compute_manager.searchResource(node_client)
                if contains == True:  # # get host list from compute resource
                    resource = self.compute_manager.getResource(pool_id, node_client)
                    for host_id in resource.allocated:
                        host_in_node.append((host_id, node_client))
                else:  # #get host list from config manager if target node_client is not in any compute pool. normally, the host list will be empty
                    host_list = self.config_manager.queryHosts(node_client)
                    for host in host_list:
                        host_in_node.append((host.uuid, node_client))

            self.info("[%08X] <query_host> success, %d host(s) in server '%s'" %
                      (session.session_id, len(host_in_node), target))

        elif target_range == 2:  # # query host in the compute node (node_client)
            if not self.service_manager.containsService(target):
                self.error("[%08X] <query_host> fail, invalid node name '%s'" %
                           (session.session_id, target))
                self.taskFail(session)
                return

            service = self.service_manager.getService(target)
            if service.type != NodeTypeDefine.node_client:
                self.error("[%08X] <query_host> fail, target '%s' is not a compute node" %
                           (session.session_id, target))
                self.taskFail(session)
                return

            contains, pool_id = self.compute_manager.searchResource(target)
            if contains == True:  # # get host list from compute resource
                compute_resource = self.compute_manager.getResource(pool_id, target)
                for host_id in compute_resource.allocated:
                    host_in_node.append((host_id, target))
            else:  # #get host list from config manager if target node_client is not in any compute pool. normally, the host list will be empty
                host_list = self.config_manager.queryHosts(target)
                for host in host_list:
                    host_in_node.append((host.uuid, target))

            self.info("[%08X] <query_host> success, %d host(s) in compute node '%s'" %
                      (session.session_id, len(host_in_node), target))

        else:
            self.error("[%08X] <query_host> fail, invalid range '%d'" %
                       (session.session_id, target_range))
            self.taskFail(session)
            return

        uuid = []
        name = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        ip = []
        status = []

        for host_id, node_client in host_in_node:
            uuid.append(host_id)
            if self.config_manager.containsHost(host_id):
                host_info = self.config_manager.getHost(host_id)
                name.append(host_info.name)

                host_ip = []  # [server_ip, public_ip or vpc_ip]
                host_ip.append(host_info.server_ip)
                if host_info.public_ip:
                    host_ip.append(host_info.public_ip)
                elif host_info.vpc_ip:
                    host_ip.append(host_info.vpc_ip)
                else:
                    host_ip.append("")

                ip.append(host_ip)
            else:
                name.append("")
                ip.append(["", ""])

            if self.status_manager.containsHostStatus(host_id):
                host_status = self.status_manager.getHostStatus(host_id)
                cpu_count.append(host_status.cpu_count)
                cpu_usage.append(host_status.cpu_usage)
                memory.append(host_status.memory)
                memory_usage.append(host_status.memory_usage)
                disk_volume.append(host_status.disk_volume)
                disk_usage.append(host_status.disk_usage)
                status.append(host_status.status)
            else:
                host_status = HostStatus()
                cpu_count.append(host_status.cpu_count)
                cpu_usage.append(host_status.cpu_usage)
                memory.append(host_status.memory)
                memory_usage.append(host_status.memory_usage)
                disk_volume.append(host_status.disk_volume)
                disk_usage.append(host_status.disk_usage)

                status.append(HostStatusEnum.status_error)
                self.warn("[%08X] <query_host> no host status available for host '%s' in resource '%s'" %
                          (session.session_id, host_id, node_client))

        response = getResponse(RequestDefine.query_host)
        response.session = session.request_session
        response.success = True

        response.setStringArray(ParamKeyDefine.name, name)
        response.setStringArray(ParamKeyDefine.uuid, uuid)
        response.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
        response.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
        response.setUIntArrayArray(ParamKeyDefine.memory, memory)
        response.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
        response.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
        response.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
        response.setStringArrayArray(ParamKeyDefine.ip, ip)
        response.setUIntArray(ParamKeyDefine.status, status)

        self.sendMessage(response, session.request_module)
        session.finish()


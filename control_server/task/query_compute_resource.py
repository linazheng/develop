#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from compute_resource import *
from service_status import ServiceStatus

class QueryComputeResourceTask(BaseTask):

    def __init__(self, task_type, messsage_handler,
                 config_manager, status_manager, compute_pool_manager, service_manager):
        self.config_manager = config_manager
        self.status_manager = status_manager
        self.service_manager = service_manager
        self.compute_pool_manager = compute_pool_manager
        logger_name = "task.query_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.query_compute_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)

        name = []
        status = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        ip = []

        if bool(pool):
            if not self.compute_pool_manager.containsPool(pool):
                self.error("[%08X] query compute resource fail, invalid pool id '%s'" %
                           (session.session_id, pool))
                self.taskFail(session)
                return

            resource_list = self.compute_pool_manager.queryResource(pool)
            for resource in resource_list:
                name.append(resource.name)
                if self.service_manager.containsService(resource.name):
                    status.append(self.service_manager.getService(resource.name).status)
                else:
                    status.append(ServiceStatus.status_stop)

                server_id = resource.server
                if self.status_manager.containsServerStatus(server_id):
                    server = self.status_manager.getServerStatus(server_id)
                    cpu_count.append(server.cpu_count)
                    cpu_usage.append(server.cpu_usage)
                    memory.append(server.memory)
                    memory_usage.append(server.memory_usage)
                    disk_volume.append(server.disk_volume)
                    disk_usage.append(server.disk_usage)
                    ip.append(server.ip)
                else:
                    cpu_count.append(0)
                    cpu_usage.append(0.0)
                    memory.append([0, 0])
                    memory_usage.append(0.0)
                    disk_volume.append([0, 0])
                    disk_usage.append(0)
                    if self.config_manager.containsServer(server_id):
                        server_info = self.config_manager.getServer(server_id)
                        ip.append(server_info.ip)
                    else:
                        ip.append("")

            self.info("[%08X]query compute resource success, %d compute resource(s) available" %
                      (session.session_id, len(resource_list)))
        else:
            # get all service group
            for service_group in self.service_manager.queryServiceGroup(NodeTypeDefine.node_client):
                # get all service
                for service in self.service_manager.queryService(NodeTypeDefine.node_client, service_group):
                    # search service in compute pool
                    node_in_pool, pool_id = self.compute_pool_manager.searchResource(service.name)
                    # service not in compute pool
                    if not node_in_pool:
                        name.append(service.name)
                        status.append(service.status)

                        server_id = service.server
                        if self.status_manager.containsServerStatus(server_id):
                            server = self.status_manager.getServerStatus(server_id)
                            cpu_count.append(server.cpu_count)
                            cpu_usage.append(server.cpu_usage)
                            memory.append(server.memory)
                            memory_usage.append(server.memory_usage)
                            disk_volume.append(server.disk_volume)
                            disk_usage.append(server.disk_usage)
                            ip.append(server.ip)
                        else:
                            cpu_count.append(0)
                            cpu_usage.append(0.0)
                            memory.append([0, 0])
                            memory_usage.append(0.0)
                            disk_volume.append([0, 0])
                            disk_usage.append(0)
                            ip.append(service.ip)
            self.info("[%08X]query compute resource success, %d deallocated compute resource(s) available" %
                      (session.session_id, len(name)))

        response = getResponse(RequestDefine.query_compute_resource)
        response.session = session.request_session
        response.success = True

        response.setStringArray(ParamKeyDefine.name, name)
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
        response.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
        response.setUIntArrayArray(ParamKeyDefine.memory, memory)
        response.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
        response.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
        response.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)
        response.setStringArray(ParamKeyDefine.ip, ip)


        self.sendMessage(response, session.request_module)
        session.finish()

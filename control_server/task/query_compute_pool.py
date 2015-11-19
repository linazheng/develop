#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from compute_pool import *
from compute_pool_status import ComputePoolStatus

class QueryComputePoolTask(BaseTask):
    
    def __init__(self, task_type, messsage_handler, status_manager, compute_pool_manager):
        self.status_manager = status_manager
        self.compute_pool_manager = compute_pool_manager
        logger_name = "task.query_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_compute_pool, messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        pool_list = self.compute_pool_manager.queryAllPool()
        
        name = []
        uuid = []
        node = []
        host = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []        
        status = []
        
        for compute_pool in pool_list:
            if self.status_manager.containsComputePoolStatus(compute_pool.uuid):
                pool = self.status_manager.getComputePoolStatus(compute_pool.uuid)
            else:
                pool = ComputePoolStatus()
                pool.name = compute_pool.name
                pool.uuid = compute_pool.uuid
                pool.status = compute_pool.status

            name.append(pool.name)
            uuid.append(pool.uuid)
            node.append(pool.node)
            host.append(pool.host)
            cpu_count.append(pool.cpu_count)
            cpu_usage.append(pool.cpu_usage)
            memory.append(pool.memory)
            memory_usage.append(pool.memory_usage)
            disk_volume.append(pool.disk_volume)
            disk_usage.append(pool.disk_usage)
            status.append(pool.status)
            

        self.info("[%08X] <query_compute_pool> success, %d compute pool(s) available" % (session.session_id, len(pool_list)))
        
        response = getResponse(RequestDefine.query_compute_pool)
        response.session = session.request_session
        response.success = True
        response.setStringArray(ParamKeyDefine.name, name)
        response.setStringArray(ParamKeyDefine.uuid, uuid)
        response.setUIntArrayArray(ParamKeyDefine.node, node)
        response.setUIntArrayArray(ParamKeyDefine.host, host)
        response.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)
        response.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)
        response.setUIntArrayArray(ParamKeyDefine.memory, memory)
        response.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)
        response.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)
        response.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)

        response.setUIntArray(ParamKeyDefine.status, status)
        
        self.sendMessage(response, session.request_module)
        session.finish()

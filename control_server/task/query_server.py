#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from status_enum import *

class QueryServerTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager, config_manager):
        self.config_manager = config_manager
        self.status_manager = status_manager
        logger_name = "task.query_server"
        BaseTask.__init__(self, task_type, RequestDefine.query_server,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        rack_id = session.initial_message.getString(ParamKeyDefine.rack)
        server_list = self.config_manager.queryServers(rack_id)
        count = len(server_list)
        
        response = getResponse(RequestDefine.query_server)
        response.session = session.request_session
        response.success = True

        name = []
        uuid = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        status = []
        ip = []
        for server in server_list:
            if self.status_manager.containsServerStatus(server.uuid):
                server_status = self.status_manager.getServerStatus(server.uuid)
                name.append(server.name)
                uuid.append(server_status.uuid)
                cpu_count.append(server_status.cpu_count)
                cpu_usage.append(server_status.cpu_usage)
                memory.append(server_status.memory)
                memory_usage.append(server_status.memory_usage)
                disk_volume.append(server_status.disk_volume)
                disk_usage.append(server_status.disk_usage)
                status.append(server_status.status)
                ip.append(server_status.ip)
            else:
                ##stopped
                name.append(server.name)
                uuid.append(server.uuid)                
                cpu_count.append(0)
                cpu_usage.append(0.0)
                memory.append([0, 0])
                memory_usage.append(0.0)
                disk_volume.append([0, 0])
                disk_usage.append(0.0)
                status.append(StatusEnum.stop)
                ip.append(server.ip)

        response.setStringArray(ParamKeyDefine.name, name)            
        response.setStringArray(ParamKeyDefine.uuid, uuid)                    
        response.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)            
        response.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)            
        response.setUIntArrayArray(ParamKeyDefine.memory, memory)            
        response.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)            
        response.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)            
        response.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)            
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setStringArray(ParamKeyDefine.ip, ip)  
            
        self.info("[%08X]query server success, %d server(s) configured"%(
            session.session_id, count))
        self.sendMessage(response, session.request_module)
        session.finish()

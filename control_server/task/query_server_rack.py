#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryServerRackTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager, config_manager):
        self.config_manager = config_manager
        self.status_manager = status_manager
        logger_name = "task.query_server_rack"
        BaseTask.__init__(self, task_type, RequestDefine.query_server_rack,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        room_id = session.initial_message.getString(ParamKeyDefine.room)
        rack_list = self.config_manager.queryServerRacks(room_id)
        count = len(rack_list)
        
        response = getResponse(RequestDefine.query_server_rack)
        response.session = session.request_session
        response.success = True

        name = []
        uuid = []
        server = []
        cpu_count = []
        cpu_usage = []
        memory = []
        memory_usage = []
        disk_volume = []
        disk_usage = []
        status = []
        for rack in rack_list:
            if self.status_manager.containsServerRackStatus(rack.uuid):
                rack_status = self.status_manager.getServerRackStatus(rack.uuid)
                name.append(rack_status.name)
                uuid.append(rack_status.uuid)
                server.append(rack_status.server)
                cpu_count.append(rack_status.cpu_count)
                cpu_usage.append(rack_status.cpu_usage)
                memory.append(rack_status.memory)
                memory_usage.append(rack_status.memory_usage)
                disk_volume.append(rack_status.disk_volume)
                disk_usage.append(rack_status.disk_usage)
                status.append(rack_status.status)

        response.setStringArray(ParamKeyDefine.name, name)            
        response.setStringArray(ParamKeyDefine.uuid, uuid)            
        response.setUIntArrayArray(ParamKeyDefine.server, server)            
        response.setUIntArray(ParamKeyDefine.cpu_count, cpu_count)            
        response.setFloatArray(ParamKeyDefine.cpu_usage, cpu_usage)            
        response.setUIntArrayArray(ParamKeyDefine.memory, memory)            
        response.setFloatArray(ParamKeyDefine.memory_usage, memory_usage)            
        response.setUIntArrayArray(ParamKeyDefine.disk_volume, disk_volume)            
        response.setFloatArray(ParamKeyDefine.disk_usage, disk_usage)            
        response.setUIntArray(ParamKeyDefine.status, status)            
            
        self.info("[%08X]query server rack success, %d rack(s) configured"%(
            session.session_id, count))
        self.sendMessage(response, session.request_module)
        session.finish()

#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from status_enum import *

class QueryServerRoomTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager, config_manager):
        self.status_manager = status_manager
        self.config_manager = config_manager
        logger_name = "task.query_server_room"
        BaseTask.__init__(self, task_type, RequestDefine.query_server_room,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        room_list = self.config_manager.queryAllServerRooms()
        count = len(room_list)
        response = getResponse(RequestDefine.query_server_room)
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
        for room in room_list:
            if self.status_manager.containsServerRoomStatus(room.uuid):
                room_status = self.status_manager.getServerRoomStatus(room.uuid)
                name.append(room_status.name)
                uuid.append(room_status.uuid)
                server.append(room_status.server)
                cpu_count.append(room_status.cpu_count)
                cpu_usage.append(room_status.cpu_usage)
                memory.append(room_status.memory)
                memory_usage.append(room_status.memory_usage)
                disk_volume.append(room_status.disk_volume)
                disk_usage.append(room_status.disk_usage)
                status.append(room_status.status)
            else:
                name.append(room.name)
                uuid.append(room.uuid)
                server.append([0, 0, 0, 0])
                cpu_count.append(0)
                cpu_usage.append(0.0)
                memory.append([0, 0])
                memory_usage.append(0.0)
                disk_volume.append([0, 0])
                disk_usage.append(0.0)
                status.append(StatusEnum.stop)                

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
            
        self.info("[%08X]query server room success, %d room(s) configured"%(
            session.session_id, count))
        self.sendMessage(response, session.request_module)
        session.finish()

#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *

from server_room_info import *
from server_rack_info import *
from server_info import *

class LoadConfigTask(BaseTask):
    query_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager):
        self.config_manager = config_manager
        logger_name = "task.load_config"
        BaseTask.__init__(self, task_type, RequestDefine.load_config,
                          messsage_handler, logger_name)

        ##state rule define, state id from 1
        stQueryRack = 2
        stQueryServer = 3
        
        self.addState(stQueryRack)
        self.addState(stQueryServer)
        
        self.stQueryServer = stQueryServer
        
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server_room, result_success,
                             self.onQueryRoomSuccess, stQueryRack)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.query_server_room, result_fail,
                             self.onQueryRoomFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryRoomTimeout)
        
        self.addTransferRule(stQueryRack, AppMessage.RESPONSE,
                             RequestDefine.query_server_rack, result_success,
                             self.onQueryRackSuccess, stQueryRack)
        self.addTransferRule(stQueryRack, AppMessage.RESPONSE,
                             RequestDefine.query_server_rack, result_fail,
                             self.onQueryRackFail)
        self.addTransferRule(stQueryRack, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryRackTimeout)
        
        self.addTransferRule(stQueryServer, AppMessage.RESPONSE,
                             RequestDefine.query_server, result_success,
                             self.onQueryServerSuccess, stQueryServer)
        self.addTransferRule(stQueryServer, AppMessage.RESPONSE,
                             RequestDefine.query_server, result_fail,
                             self.onQueryServerFail)
        self.addTransferRule(stQueryServer, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onQueryServerTimeout)
        

    def invokeSession(self, session):
        """
        task start, must override
        """
        session.data_server = getString(session.initial_message, ParamKeyDefine.target)
        request = getRequest(RequestDefine.query_server_room)
        request.session = session.session_id
        self.sendMessage(request, session.data_server)
        
        self.setTimer(session, self.query_timeout)
        self.info("[%08X]try load config from data server '%s'..."%(
            session.session_id, session.data_server))

    def onQueryRoomSuccess(self, response, session):
        self.clearTimer(session)
        name = response.getStringArray(ParamKeyDefine.name)
        domain = response.getStringArray(ParamKeyDefine.domain)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        display = response.getStringArray(ParamKeyDefine.display)
        description = response.getStringArray(ParamKeyDefine.description)
        count = len(uuid)        
        if 0 == count:
            self.info("[%08X]query server room success, no server room available"%session.session_id)
            session.finish()
            return

        data_list = []
        for i in range(count):
            info = ServerRoomInfo()
            info.name = name[i]
            info.domain = domain[i]
            info.uuid = uuid[i]
            info.display = display[i]
            info.description = description[i]
            data_list.append(info)
            
        self.config_manager.loadServerRooms(data_list)
        self.info("[%08X]query server room success, %d server room(s) available"%(
            session.session_id, count))
        ##query rack
        session.target_list = uuid
        session.result_list = []
        session.total = count
        session.offset = 0

        room_id = session.target_list[session.offset]
        self.info("[%08X]query server racks in server room '%s'..."%(
            session.session_id, room_id))
        request = getRequest(RequestDefine.query_server_rack)
        request.session = session.session_id
        request.setString(ParamKeyDefine.room, room_id)
        
        self.sendMessage(request, session.data_server)
        self.setTimer(session, self.query_timeout)

    def onQueryRoomFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query server room fail"%session.session_id)
        session.finish()

    def onQueryRoomTimeout(self, response, session):
        self.info("[%08X]query server room timeout"%session.session_id)
        session.finish()

    def onQueryRackSuccess(self, response, session):
        self.clearTimer(session)
        room_id = session.target_list[session.offset]
        
        name = response.getStringArray(ParamKeyDefine.name)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        count = len(uuid)        
        if 0 != count:
            data_list = []
            for i in range(count):
                info = ServerRackInfo()
                info.name = name[i]
                info.uuid = uuid[i]
                info.server_room = room_id
                data_list.append(info)
                
            self.config_manager.loadServerRacks(room_id, data_list)
            session.result_list.extend(uuid)
            self.info("[%08X]query server rack success, %d server rack(s) available in room '%s'"%(
                session.session_id, count, room_id))
        
        else:
            self.info("[%08X]query server rack success, no server rack available in room '%s'"%
                      (session.session_id, room_id))
        ##is last room?
        session.offset += 1
        if session.offset != session.total:
            ##query rack for next room
            room_id = session.target_list[session.offset]
            self.info("[%08X]query server racks in server room '%s'..."%(
                session.session_id, room_id))
            request = getRequest(RequestDefine.query_server_rack)
            request.session = session.session_id
            request.setString(ParamKeyDefine.room, room_id)
            
            self.sendMessage(request, session.data_server)
            self.setTimer(session, self.query_timeout)            
        else:
            ##begin query server
            count = len(session.result_list)
            if 0 == count:
                ##no rack available
                self.info("[%08X]load config finish, no server rack available in system"%
                      (session.session_id))
                session.fisish()
                return
            
            session.target_list = session.result_list
            session.result_list = []
            session.total = count
            session.offset = 0
            ##for state
            session.setState(self.stQueryServer)

            rack_id = session.target_list[session.offset]
            self.info("[%08X]query server in server rack '%s'..."%(
                session.session_id, rack_id))
            request = getRequest(RequestDefine.query_server)
            request.session = session.session_id
            request.setString(ParamKeyDefine.rack, rack_id)
            
            self.sendMessage(request, session.data_server)
            self.setTimer(session, self.query_timeout)


    def onQueryRackFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query server rack fail"%session.session_id)
        session.finish()

    def onQueryRackTimeout(self, response, session):
        self.info("[%08X]query server rack timeout"%session.session_id)
        session.finish()
    
    def onQueryServerSuccess(self, response, session):
        self.clearTimer(session)
        rack_id = session.target_list[session.offset]
        
        name = response.getStringArray(ParamKeyDefine.name)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        mac = response.getStringArray(ParamKeyDefine.ethernet_address)
        ip = response.getStringArray(ParamKeyDefine.ip)
        
        count = len(uuid)        
        if 0 != count:
            data_list = []
            for i in range(count):
                info = ServerInfo()
                info.name = name[i]
                info.uuid = uuid[i]
                info.rack = rack_id
                info.ip = ip[i]
                data_list.append(info)
                
            self.config_manager.loadServers(rack_id, data_list)
            
            self.info("[%08X]query server success, %d server(s) available in rack '%s'"%(
                session.session_id, count, rack_id))
        
        else:
            self.info("[%08X]query server success, no server available in rack '%s'"%
                      (session.session_id, rack_id))
        ##is last rack?
        session.offset += 1
        if session.offset != session.total:
            ##query rack for next rack
            rack_id = session.target_list[session.offset]
            self.info("[%08X]query server in server rack '%s'..."%(
                session.session_id, rack_id))
            request = getRequest(RequestDefine.query_server)
            request.session = session.session_id
            request.setString(ParamKeyDefine.rack, rack_id)
            
            self.sendMessage(request, session.data_server)
            self.setTimer(session, self.query_timeout)
        else:
            ##finish
            self.info("[%08X]load config finish, all server loaded"%
                      (session.session_id))
            session.finish()
            return
        
    def onQueryServerFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query server fail"%session.session_id)
        session.finish()
        
    def onQueryServerTimeout(self, response, session):
        self.info("[%08X]query server timeout"%session.session_id)
        session.finish()
    

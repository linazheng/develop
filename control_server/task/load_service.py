#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *

from service_status import *

class LoadServiceTask(BaseTask):
    query_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 service_manager):
        self.service_manager = service_manager
        logger_name = "task.load_service"
        BaseTask.__init__(self, task_type, RequestDefine.invalid,
                          messsage_handler, logger_name)

        ##state rule define, state id from 1
        stQueryService = 2
        
        self.addState(stQueryService)                
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_service_type, result_success, self.onQueryTypeSuccess, stQueryService)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_service_type, result_fail,    self.onQueryTypeFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,              result_any,     self.onQueryTypeTimeout)        
        
        # stQueryService
        self.addTransferRule(stQueryService, AppMessage.RESPONSE, RequestDefine.query_service, result_success, self.onQueryServiceSuccess, stQueryService)
        self.addTransferRule(stQueryService, AppMessage.RESPONSE, RequestDefine.query_service, result_fail,    self.onQueryServiceFail)
        self.addTransferRule(stQueryService, AppMessage.EVENT,    EventDefine.timeout,         result_any,     self.onQueryServiceTimeout)
        

    def invokeSession(self, session):
        """
        task start, must override
        """
        session.data_server = getString(session.initial_message, ParamKeyDefine.target)
        request = getRequest(RequestDefine.query_service_type)
        request.session = session.session_id
        self.sendMessage(request, session.data_server)
        
        self.setTimer(session, self.query_timeout)
        self.info("[%08X]try load service from data server '%s'..."%(
            session.session_id, session.data_server))

    def onQueryTypeSuccess(self, response, session):
        self.clearTimer(session)
        type_array = response.getUIntArray(ParamKeyDefine.type)
        count = len(type_array)        
        if 0 == count:
            self.info("[%08X]query service type success, no service available"%session.session_id)
            session.finish()
            return

        self.info("[%08X]query service type success, %d service type(s) available"%(
            session.session_id, count))
        ##query service
        session.target_list = type_array
        session.total = count
        session.offset = 0

        service_type = session.target_list[session.offset]
        self.info("[%08X]query service in type %d ..."%(
            session.session_id, service_type))
        
        request = getRequest(RequestDefine.query_service)
        request.session = session.session_id
        request.setUInt(ParamKeyDefine.type, service_type)
        ##only default group
        request.setString(ParamKeyDefine.group, "default")
        
        self.sendMessage(request, session.data_server)
        self.setTimer(session, self.query_timeout)

    def onQueryTypeFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query service type fail"%session.session_id)
        session.finish()

    def onQueryTypeTimeout(self, response, session):
        self.info("[%08X]query service type timeout"%session.session_id)
        session.finish()
    
    def onQueryServiceSuccess(self, response, session):
        self.clearTimer(session)
        service_type = session.target_list[session.offset]
        
        name = response.getStringArray(ParamKeyDefine.name)
        ip = response.getStringArray(ParamKeyDefine.ip)
        port = response.getUIntArray(ParamKeyDefine.port)
        version = response.getStringArray(ParamKeyDefine.version)
        status = response.getUIntArray(ParamKeyDefine.status)
        server = response.getStringArray(ParamKeyDefine.server)
        
        count = len(name)        
        if 0 != count:
            data_list = []
            for i in range(count):
                info = ServiceStatus()
                info.name = name[i]
                info.ip = ip[i]
                info.port = port[i]
                info.version = version[i]
                info.status = status[i]
                info.server = server[i]
                info.group = "default"
                info.type = service_type
                
                data_list.append(info)
                
            self.service_manager.loadService(service_type, data_list)
            
            self.info("[%08X]query service success, %d service(s) available in type %d"%(
                session.session_id, count, service_type))
        
        else:
            self.info("[%08X]query service success, no service available in type %d"%
                      (session.session_id, service_type))
        ##is last type?
        session.offset += 1
        if session.offset != session.total:
            ##query service for next type
            service_type = session.target_list[session.offset]
            self.info("[%08X]query service in type %d ..."%(
                session.session_id, service_type))
            
            request = getRequest(RequestDefine.query_service)
            request.session = session.session_id
            request.setUInt(ParamKeyDefine.type, service_type)
            ##only default group
            request.setString(ParamKeyDefine.group, "default")
            
            self.sendMessage(request, session.data_server)
            self.setTimer(session, self.query_timeout)
        else:
            ##finish
            self.info("[%08X]load service finish, all service type loaded"%
                      (session.session_id))
            session.finish()
            return
        
    def onQueryServiceFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]query service fail"%session.session_id)
        session.finish()
        
    def onQueryServiceTimeout(self, response, session):
        self.info("[%08X]query service timeout"%session.session_id)
        session.finish()
    

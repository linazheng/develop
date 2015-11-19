#!/usr/bin/python
# -*- coding: utf-8 -*-

from transaction.base_task import BaseTask
from service.message_define import RequestDefine, getResponse, ParamKeyDefine

class QueryNetworkDetailTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager):
        self.network_manager = network_manager
        logger_name = "task.query_network_detail"
        BaseTask.__init__(self, task_type, RequestDefine.query_network_detail, messsage_handler, logger_name)
    
    
    def invokeSession(self, session):
        request = session.initial_message
        
        uuid = request.getString(ParamKeyDefine.uuid)
        
        _networkInfo = self.network_manager.getNetwork(uuid)
        if _networkInfo==None:
            self.warn("[%08X] <query_network_detail> query network detail fail, invalid id '%s'" % (session.session_id, uuid))
            self.taskFail(session)
            return
        
        self.info("[%08X] <query_network_detail> query network detail success" % (session.session_id))
        
        response = getResponse(RequestDefine.query_network_detail)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.uuid,            _networkInfo.uuid)
        response.setString(ParamKeyDefine.name,            _networkInfo.name)
        response.setUInt(ParamKeyDefine.size,              _networkInfo.size)
        response.setString(ParamKeyDefine.network_address, _networkInfo.network_address)
        response.setUInt(ParamKeyDefine.netmask,           _networkInfo.netmask)
        response.setString(ParamKeyDefine.description,     _networkInfo.description)
        response.setUInt(ParamKeyDefine.status,            _networkInfo.status)
        response.setStringArray(ParamKeyDefine.ip,         [ip for ip in _networkInfo.public_ips])
        
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
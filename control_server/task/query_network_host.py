#!/usr/bin/python
# -*- coding: utf-8 -*-


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, getResponse, ParamKeyDefine


class QueryNetworkHostTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager, config_manager):
        self.network_manager = network_manager
        self.config_manager = config_manager
        logger_name = "task.query_network_host"
        BaseTask.__init__(self, task_type, RequestDefine.query_network_host, messsage_handler, logger_name)
    
    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"] = request.getString(ParamKeyDefine.uuid)
        
        self.warn("[%08X] <query_network_host> receive query network host request, uuid '%s'" % (session.session_id, _parameter["uuid"]))
        
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.warn("[%08X] <query_network_host> query network host fail, invalid network uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        uuidArr = []
        nameArr = []
        networkAddressArr = []
        
        for _host_uuid in _networkInfo.hosts:
            _host = self.config_manager.getHost(_host_uuid)
            if _host==None:
                continue
            uuidArr.append(_host_uuid)
            nameArr.append(_host.name)
            networkAddressArr.append(_host.vpc_ip)
            
        self.info("[%08X] <query_network_host> query attach host success, %d attached host(s) available" % (session.session_id, len(uuidArr)))
        
        response = getResponse(RequestDefine.query_network_host)
        response.session = session.request_session
        
        response.success = True
        
        response.setStringArray(ParamKeyDefine.uuid, uuidArr)
        response.setStringArray(ParamKeyDefine.name, nameArr)
        response.setStringArray(ParamKeyDefine.network_address, networkAddressArr)
        
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
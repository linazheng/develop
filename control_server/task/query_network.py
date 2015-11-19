#!/usr/bin/python
# -*- coding: utf-8 -*-

from transaction.base_task import BaseTask
from service.message_define import RequestDefine, getResponse, ParamKeyDefine

class QueryNetworkTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager):
        self.network_manager = network_manager
        logger_name = "task.query_network"
        BaseTask.__init__(self, task_type, RequestDefine.query_network, messsage_handler, logger_name)
    
    
    def invokeSession(self, session):
        _network_list = self.network_manager.getAllNetworks()
        
        if 0 == len(_network_list):
            self.warn("[%08X] <query_network> query network fail, no network available" % session.session_id)
            self.taskFail(session)
            return
        
        _uuidArr = []
        _nameArr = []
        _networkAddressArr = []
        _netmaskArr = []
        for _network in _network_list:
            _uuidArr.append(_network.uuid)
            _nameArr.append(_network.name)
            _networkAddressArr.append(_network.network_address)
            _netmaskArr.append(_network.netmask)
            

        self.info("[%08X] <query_network> query network success, %d network(s) available" % (session.session_id, len(_network_list)))
        
        response = getResponse(RequestDefine.query_network)
        response.session = session.request_session
        response.success = True
        
        response.setStringArray(ParamKeyDefine.uuid, _uuidArr)
        response.setStringArray(ParamKeyDefine.name, _nameArr)
        response.setStringArray(ParamKeyDefine.network_address, _networkAddressArr)
        response.setUIntArray(ParamKeyDefine.netmask, _netmaskArr)
        
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
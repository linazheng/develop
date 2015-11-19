#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse,\
    getRequest, EventDefine
from network_info import NetworkStatus
from __builtin__ import IndexError
from common import dict_util
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage


class StopNetworkTask(BaseTask):
    
    
    operate_timeout = 10
    
    
    def __init__(self, task_type, messsage_handler, network_manager, config_manager, forwarder_manager):
        self.network_manager    = network_manager
        self.config_manager     = config_manager
        self.forwarder_manager  = forwarder_manager
        logger_name = "task.stop_network"
        BaseTask.__init__(self, task_type, RequestDefine.stop_network, messsage_handler, logger_name)
        
        stSetForwarderStatusSuccess = 2
        self.addState(stSetForwarderStatusSuccess)
        
        # state_initial
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_success, self.onStatusSuccess, stSetForwarderStatusSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_fail,    self.onStatusFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,                result_any,     self.onStatusTimeout)        

        # stSetForwarderStatusSuccess
        self.addTransferRule(stSetForwarderStatusSuccess, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_success, self.onStatusSuccess, stSetForwarderStatusSuccess)
        self.addTransferRule(stSetForwarderStatusSuccess, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_fail,    self.onStatusFail)
        self.addTransferRule(stSetForwarderStatusSuccess, AppMessage.EVENT,    EventDefine.timeout,                result_any,     self.onStatusTimeout)        

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        session._ext_data = {}
        
        _parameter = {}
        _parameter["uuid"] = request.getString(ParamKeyDefine.uuid)
        
        session._ext_data["parameter"] = _parameter
        
        self.info("[%08X] <stop_network> receive stop network request from '%s', uuid: %s" % (session.session_id, 
                                                                                              session.request_module, 
                                                                                              _parameter["uuid"]))
        
        
        # get default ir
        _default_ir = self.message_handler.getDefaultIntelligentRouter()
        if _default_ir == None:
            self.warn("[%08X] <stop_network> stop network fail, no intelligent router actived"%(session.session_id))
        
        session._ext_data["default_ir"] = _default_ir
        
        
        # get network_info
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <stop_network> stop network fail, invalid network uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        _networkInfo.status = NetworkStatus.disabled
        self.network_manager.saveNetworkInfo(_parameter["uuid"])
        
        
        #
        _hosts = []
        _hostUUIDs = _networkInfo.hosts.copy()
        for _host_uuid in _hostUUIDs:
            _host = self.config_manager.getHost(_host_uuid)
            if _host==None:
                self.warn("[%08X] <stop_network> invalid host uuid '%s'" % (session.session_id, _host_uuid))
                continue
            _hosts.append(_host)
        
        # 
        _forwarders = []
        for _host in _hosts:
            if _host.forwarder:
                _forwarder = self.forwarder_manager.get(_host.forwarder)
                if _forwarder and _forwarder.enable==True:
#                     _forwarder.enable = False
                    self.forwarder_manager.disable(_forwarder.uuid)
                    _forwarders.append(_forwarder)
                    
        session._ext_data["forwarders"] = _forwarders
        
        self._sendToDisableForwarders(session)
            
        


        
    def _sendToDisableForwarders(self, session):
        
        _forwarders = session._ext_data["forwarders"]
        _default_ir = session._ext_data["default_ir"]
         
        try:
            _forwarder = _forwarders.pop()
            session._ext_data["forwarder"] = _forwarder
        except IndexError:
            self.info("[%08X] <stop_network> no more forwarder in network to delete." % (session.session_id))
            self._sendResponse(session);
            return ;
        
        # set forwarder status
        set_forwarder_request = getRequest(RequestDefine.set_forwarder_status)
        set_forwarder_request.session = session.session_id
        
        set_forwarder_request.setString(ParamKeyDefine.uuid, _forwarder.uuid)
        set_forwarder_request.setUInt(ParamKeyDefine.status, 0)
        
        self.sendMessage(set_forwarder_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
        
        
    #----------------------------
    
    
    def onStatusSuccess(self, msg, session):
        self.clearTimer(session)
        
        _default_ir  = session._ext_data["default_ir"] 
        _forwarder   = session._ext_data["forwarder"] 
        
        self.info("[%08X] <stop_network> disable forwarder in intelligent router success, forwarder id '%s'"% (session.session_id, _forwarder.uuid))
        self._sendToDisableForwarders(session)
        

    def onStatusFail(self, msg, session):
        self.clearTimer(session)
        _forwarder   = session._ext_data["forwarder"] 
        self.error("[%08X] <stop_network> disable forwarder in intelligent router fail, forwarder id '%s'"% (session.session_id, _forwarder.uuid))
        self.taskFail(session)
        
        
    def onStatusTimeout(self, msg, session):
        _forwarder   = session._ext_data["forwarder"] 
        self.error("[%08X] <stop_network> disable forwarder in intelligent router timeout, forwarder id '%s'"% (session.session_id, _forwarder.uuid))
        self.taskFail(session)
    
    
    #------------------------------ 
        
         
    def _sendResponse(self, session):
        _parameter = session._ext_data["parameter"]
        
        self.info("[%08X] <stop_network> stop network success, uuid '%s'" % (session.session_id, _parameter["uuid"]))
         
        response = getResponse(RequestDefine.stop_network)
        response.session = session.request_session
        response.success = True
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
        
        
        
        
        
        
        
        
        
        
        


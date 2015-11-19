#!/usr/bin/python
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, EventDefine, getRequest,\
    ParamKeyDefine
from transaction.state_define import state_initial, result_success, result_fail,\
    result_any
from transport.app_message import AppMessage

class SetForwarderStatusTask(BaseTask):
    
    operate_timeout = 5
    
    def __init__(self, task_type, messsage_handler, forwarder_manager):
        self.forwarder_manager = forwarder_manager
        logger_name = "task.set_forwarder_status"
        BaseTask.__init__(self, task_type, RequestDefine.set_forwarder_status, messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_success, self.onStartSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.set_forwarder_status, result_fail,    self.onStartFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,                result_any,     self.onStartTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        
        session._ext_data = {}
        
        #
        _parameter = {}
        _parameter["uuid"]   = request.getString(ParamKeyDefine.uuid)
        _parameter["status"] = request.getUInt(ParamKeyDefine.status)   # 0:disable, 1:enable
        
        session._ext_data["parameter"] = _parameter
        
        #
        forwarder_id = _parameter["uuid"] 
        status       = _parameter["status"] 
        
        # get default ir
        _default_ir = self.message_handler.getDefaultIntelligentRouter()
        if _default_ir == None:
            self.warn("[%08X] <set_forwarder_status> set forwarder status fail, no intelligent router actived" % (session.session_id))
        
        session._ext_data["default_ir"] = _default_ir
        
        # send set forwarder status
        set_status_request = getRequest(RequestDefine.set_forwarder_status)
        set_status_request.session = session.session_id
        
        set_status_request.setString(ParamKeyDefine.uuid, forwarder_id)
        set_status_request.setUInt(ParamKeyDefine.status, status)
        
        self.sendMessage(set_status_request, _default_ir)
        self.setTimer(session, self.operate_timeout)
    
        
    #----------------------
    

    def onStartSuccess(self, msg, session):
        self.clearTimer(session)
        _parameter = session._ext_data["parameter"] 
        self.info("[%08X] <set_forwarder_status> set forwarder status success, id '%s'" % (session.session_id, _parameter["uuid"]))
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()


    def onStartFail(self, msg, session):
        self.clearTimer(session)
        _parameter = session._ext_data["parameter"] 
        self.info("[%08X] <set_forwarder_status> set forwarder status fail, id '%s'" % (session.session_id, _parameter["uuid"]))
        self.taskFail(session)
        
        
    def onStartTimeout(self, msg, session):
        _parameter = session._ext_data["parameter"] 
        self.info("[%08X] <set_forwarder_status> set forwarder status timeout, id '%s'" % (session.session_id, _parameter["uuid"]))
        self.taskFail(session)

        
    #----------------------
    
        
        
        
        
        
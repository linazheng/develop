#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from host_info import *
from host_forwarder import *

class RemoveForwarderTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager, compute_pool_manager,
                 address_manager, port_manager,
                 forwarder_manager):
        self.config_manager = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.address_manager = address_manager
        self.port_manager = port_manager
        self.forwarder_manager = forwarder_manager
        logger_name = "task.remove_forwarder"
        BaseTask.__init__(self, task_type, RequestDefine.remove_forwarder,
                          messsage_handler, logger_name)

        ##state rule define, state id from 1
        stRemoveForwarder = 2
        self.addState(stRemoveForwarder)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_success,
                             self.onDetachSuccess, stRemoveForwarder)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_fail,
                             self.onDetachFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onDetachTimeout)
        
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_success,
                             self.onRemoveSuccess)
        self.addTransferRule(stRemoveForwarder, AppMessage.RESPONSE,
                             RequestDefine.remove_forwarder, result_fail,
                             self.onRemoveFail)
        self.addTransferRule(stRemoveForwarder, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onRemoveTimeout)
        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        target_id = request.getString(ParamKeyDefine.target)
        target_type = request.getUInt(ParamKeyDefine.type)
        forwarder_id = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive remove forwarder request from '%s', target id '%s',type %d, forwarder '%s'"%(
                session.session_id, session.request_module, target_id, target_type,
                forwarder_id))
        if 1 == target_type:
            ##disk
            self.error("[%08X]remove forwarder fail, disk forwarder not supported"%(
                session.session_id))
            self.taskFail(session)
            return
        if not self.config_manager.containsHost(target_id):
            self.error("[%08X]remove forwarder fail, invalid host id '%s'"%(
                session.session_id, target_id))
            self.taskFail(session)
            return
        if not self.forwarder_manager.contains(forwarder_id):
            self.error("[%08X]remove forwarder fail, invalid forwarder id '%s'"%(
                session.session_id, forwarder_id))
            self.taskFail(session)
            return
            
        ##check ir
        default_ir = self.message_handler.getDefaultIntelligentRouter()
        if default_ir is None:
            self.error("[%08X]remove forwarder fail, no intelligent router actived"%(
                session.session_id))
            self.taskFail(session)
            return
            
        host = self.config_manager.getHost(target_id)
        
        request.session = session.session_id       
            
        self.sendMessage(request, host.container)
        self.setTimer(session, self.operate_timeout)
        session.target = forwarder_id
        
        self.info("[%08X]request remove forwarder '%s' to compute node '%s'..."%(
            session.session_id, forwarder_id, host.container))

    def onDetachSuccess(self, msg, session):
        self.clearTimer(session)
        if not self.forwarder_manager.contains(session.target):
            self.error("[%08X]attach forwarder success, but forwarder '%s' not exists"%(
                session.session_id, session.target))
            self.taskFail(session)
            return
        ##check ir
        default_ir = self.message_handler.getDefaultIntelligentRouter()
        if default_ir is None:
            self.error("[%08X]attach forwarder success, but no intelligent router actived"%(
                session.session_id))
            self.taskFail(session)
            return
        forwarder_id = session.target
        forwarder = self.forwarder_manager.get(forwarder_id)
        ##clear host info
        if self.config_manager.containsHost(forwarder.host_id):
            host = self.config_manager.getHost(forwarder.host_id)
            self.address_manager.deallocate(host.network_source, host.public_ip)
            host.public_ip = ""
            host.public_port = forwarder.public_monitor
            host.forwarder = ""
            self.info("[%08X]detach forwarder from host '%s'"%(
                session.session_id, host.name))
        ##delete forwarder
        self.forwarder_manager.delete(forwarder_id)
            
        remove_request = getRequest(RequestDefine.remove_forwarder)
        remove_request.session = session.session_id    
        remove_request.setString(ParamKeyDefine.uuid, forwarder_id)
        
        self.sendMessage(remove_request, default_ir)
        self.setTimer(session, self.operate_timeout)

        self.info("[%08X]detach forwarder success, remove forwarder from intelligent router '%s'..."%(
            session.session_id, default_ir))

    def onDetachFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]detach forwarder fail"%(
            session.session_id))
        self.taskFail(session)
        
    def onDetachTimeout(self, msg, session):
        self.error("[%08X]detach forwarder timeout"%(
            session.session_id))
        self.taskFail(session)
            
    def onRemoveSuccess(self, response, session):
        self.clearTimer(session)
        self.info("[%08X]remove forwarder from intelligent router success"%(
            session.session_id))
        response = getResponse(RequestDefine.remove_forwarder)
        response.success = True
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
    def onRemoveFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X]remove forwarder from intelligent router fail"%(
            session.session_id))
        self.taskFail(session)
        
    def onRemoveTimeout(self, msg, session):
        self.error("[%08X]remove forwarder from intelligent router timeout"%(
            session.session_id))
        self.taskFail(session)
    

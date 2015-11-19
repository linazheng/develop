#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class EjectMediaTask(BaseTask):
    operate_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 config_manager, compute_pool_manager, iso_manager):
        self.config_manager = config_manager
        self.compute_pool_manager = compute_pool_manager
        self.iso_manager = iso_manager
        logger_name = "task.eject_media"
        BaseTask.__init__(self, task_type, RequestDefine.eject_media,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.eject_media, result_success,
                             self.onEjectSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.eject_media, result_fail,
                             self.onEjectFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onEjectTimeout)        

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive eject media request from '%s', host id '%s'"%
                       (session.session_id, session.request_module, uuid))
        
        if not self.config_manager.containsHost(uuid):
            self.error("[%08X]eject media fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        ##select compute node
        host = self.config_manager.getHost(uuid)
        service_name = host.container
        
        self.info("[%08X]redirect eject media from host '%s' to compute node '%s'"%
                       (session.session_id, host.name, service_name))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, service_name)

    def onEjectSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]eject media success, host id '%s'"%
                       (session.session_id, session.target))
        
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onEjectFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]eject media fail, host id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)
        
    def onEjectTimeout(self, msg, session):
        self.info("[%08X]eject media timeout, host id '%s'"%
                  (session.session_id, session.target))
        self.taskFail(session)

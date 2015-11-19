#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from port_pool import *

class DeletePortPoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 port_manager, compute_pool_manager):
        self.port_manager = port_manager
        self.compute_pool_manager = compute_pool_manager
        logger_name = "task.delete_port_pool"
        BaseTask.__init__(self, task_type, RequestDefine.delete_port_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive delete port pool request from '%s', pool id '%s'"%(
                session.session_id, session.request_module, uuid))

        if not self.port_manager.containsPool(uuid):
            self.error("[%08X]delete port pool fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return

        pool = self.port_manager.getPool(uuid)
        pool_name = pool.name        
        if self.compute_pool_manager.containNetwork(uuid):
            self.error("[%08X]delete port pool fail, pool '%s' is used by compute pool." % (session.session_id, pool_name))
            self.taskFail(session)
            return
        
        if not self.port_manager.deletePool(uuid):
            self.error("[%08X]delete port pool fail, pool '%s'"%
                       (session.session_id, pool_name))
            self.taskFail(session)
            return        

        self.info("[%08X]delete port pool success, pool '%s'('%s')"%
                  (session.session_id, pool_name, uuid))
        
        response = getResponse(RequestDefine.delete_port_pool)
        response.session = session.request_session
        response.success = True
    
        self.sendMessage(response, session.request_module)
        session.finish()

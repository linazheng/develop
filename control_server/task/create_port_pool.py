#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from port_pool import *

class CreatePortPoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 port_manager):
        self.port_manager = port_manager
        logger_name = "task.create_port_pool"
        BaseTask.__init__(self, task_type, RequestDefine.create_port_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        config = PortPool()
        config.name = request.getString(ParamKeyDefine.name)
        self.info("[%08X]receive create port pool request from '%s', name '%s'"%(
                session.session_id, session.request_module, config.name))
        if not self.port_manager.createPool(config):
            self.error("[%08X]create port pool fail, name '%s'"%
                       (session.session_id, config.name))
            self.taskFail(session)
            return
        

        self.info("[%08X]create port pool success, pool '%s'('%s')"%
                  (session.session_id, config.name, config.uuid))
        
        response = getResponse(RequestDefine.create_port_pool)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.uuid, config.uuid)        
        self.sendMessage(response, session.request_module)
        session.finish()

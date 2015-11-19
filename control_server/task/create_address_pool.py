#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from address_pool import *

class CreateAddressPoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 address_manager):
        self.address_manager = address_manager
        logger_name = "task.create_address_pool"
        BaseTask.__init__(self, task_type, RequestDefine.create_address_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        config = AddressPool()
        config.name = request.getString(ParamKeyDefine.name)
        self.info("[%08X]receive create address pool request from '%s', name '%s'"%(
                session.session_id, session.request_module, config.name))
        if not self.address_manager.createPool(config):
            self.error("[%08X]create address pool fail, name '%s'"%
                       (session.session_id, config.name))
            self.taskFail(session)
            return
        

        self.info("[%08X]create address pool success, pool '%s'('%s')"%
                  (session.session_id, config.name, config.uuid))
        
        response = getResponse(RequestDefine.create_address_pool)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.uuid, config.uuid)        
        self.sendMessage(response, session.request_module)
        session.finish()

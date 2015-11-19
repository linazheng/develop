#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from address_pool import *

class DeleteAddressPoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 address_manager, compute_pool_manager, network_manager):
        self.address_manager = address_manager
        self.compute_pool_manager = compute_pool_manager
        self.network_manager = network_manager
        logger_name = "task.delete_address_pool"
        BaseTask.__init__(self, task_type, RequestDefine.delete_address_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        self.info("[%08X]receive delete address pool request from '%s', pool id '%s'"%(
                session.session_id, session.request_module, uuid))

        if not self.address_manager.containsPool(uuid):
            self.error("[%08X]delete address pool fail, invalid id '%s'"%
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        
        pool = self.address_manager.getPool(uuid)
        pool_name = pool.name
        
        if self.compute_pool_manager.containNetwork(uuid):
            self.error("[%08X]delete address pool fail, pool '%s' is used by compute pool." % (session.session_id, pool_name))
            self.taskFail(session)
            return
        
        if self.network_manager.containAddressPool(uuid):
            self.error("[%08X]delete address pool fail, pool '%s' is used by vpc network." % (session.session_id, pool_name))
            self.taskFail(session)
            return
        
        if not self.address_manager.deletePool(uuid):
            self.error("[%08X]delete address pool fail, pool '%s'"%
                       (session.session_id, pool_name))
            self.taskFail(session)
            return        

        self.info("[%08X]delete address pool success, pool '%s'('%s')"%
                  (session.session_id, pool_name, uuid))
        
        response = getResponse(RequestDefine.delete_address_pool)
        response.session = session.request_session
        response.success = True
    
        self.sendMessage(response, session.request_module)
        session.finish()

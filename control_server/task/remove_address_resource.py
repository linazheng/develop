#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from address_resource import *

class RemoveAddressResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 address_manager):
        self.address_manager = address_manager
        logger_name = "task.remove_address_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_address_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        
        pool_id  = request.getString(ParamKeyDefine.pool)
        ip_array = request.getStringArray(ParamKeyDefine.ip)
        
        if ip_array != None:
            resource_count = len(ip_array)
        else:
            resource_count = 0
        self.info("[%08X]receive remove address resource request from '%s', %d resource from pool '%s'"%(session.session_id, session.request_module, resource_count, pool_id))
        
        if not self.address_manager.containsPool(pool_id):
            self.error("[%08X]remove address resource fail, invalid pool id '%s'"%(session.session_id, pool_id))
            self.taskFail(session)
            return
        
        pool = self.address_manager.getPool(pool_id)
        if ip_array == None or (not pool.removeResource(ip_array)):
            self.error("[%08X]remove address resource fail, can't remove resource '%s' from pool '%s'"%(session.session_id, ip_array, pool.name))
            self.taskFail(session)
            return             

        self.info("[%08X]remove address resource success, %d resource(s) removed from pool '%s'"%(session.session_id, resource_count, pool.name))
        
        response = getResponse(RequestDefine.remove_address_resource)
        response.session = session.request_session
        response.success = True
    
        self.sendMessage(response, session.request_module)
        session.finish()

#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from address_resource import *

class AddAddressResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 address_manager):
        self.address_manager = address_manager
        logger_name = "task.add_address_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_address_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool_id = request.getString(ParamKeyDefine.pool)
        ip_array = request.getStringArray(ParamKeyDefine.ip)
        range_array = request.getUIntArray(ParamKeyDefine.range)
        resource_count = len(ip_array)
        self.info("[%08X]receive add address resource request from '%s', %d resource to pool '%s'"%(
                session.session_id, session.request_module,
                resource_count, pool_id))
        if not self.address_manager.containsPool(pool_id):
            self.error("[%08X]add address resource fail, invalid pool id '%s'"%(
                session.session_id, pool_id))
            self.taskFail(session)
            return
        
        resource_list = []
        for i in range(resource_count):
            resource_ip = ip_array[i]
            resource_range = range_array[i]
            resource = AddressResource(resource_ip, resource_range)
            resource_list.append(resource)

        pool = self.address_manager.getPool(pool_id)
        if not pool.addResource(resource_list):
            self.error("[%08X]add address resource fail, can't add resource to pool '%s'"%(
                session.session_id, pool.name))
            self.taskFail(session)
            return        

        self.info("[%08X]add address resource success, %d resource(s) add to pool '%s'"%
                  (session.session_id, resource_count, pool.name))
        
        response = getResponse(RequestDefine.add_address_resource)
        response.session = session.request_session
        response.success = True
      
        self.sendMessage(response, session.request_module)
        session.finish()

#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from port_resource import *
from service.socket_util import *

class AddPortResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 port_manager):
        self.port_manager = port_manager
        logger_name = "task.add_port_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_port_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request        = session.initial_message
        
        pool_id        = request.getString(ParamKeyDefine.pool)
        ip_array       = request.getStringArray(ParamKeyDefine.ip)
        range_array    = request.getUIntArray(ParamKeyDefine.range)
        
        if bool(ip_array):
            resource_count = len(ip_array)
        else:
            resource_count = 0
        
        self.info("[%08X]receive add port resource request from '%s', %d resource to pool '%s'"%(session.session_id, 
                                                                                              session.request_module,
                                                                                              resource_count, 
                                                                                              pool_id))
        
        if not self.port_manager.containsPool(pool_id):
            self.error("[%08X]add port resource fail, invalid pool id '%s'"%(session.session_id, 
                                                                             pool_id))
            self.taskFail(session)
            return
        
        ip_list = []
        if bool(ip_array):
            for i in range(resource_count):
                resource_ip    = ip_array[i]
                resource_range = range_array[i]
                start_int = convertAddressToInt(resource_ip)
                for j in range(resource_range):
                    ip_list.append(convertIntToAddress(start_int + j))

        pool = self.port_manager.getPool(pool_id)
        if not pool.addResource(ip_list):
            self.error("[%08X]add port resource fail, can't add resource to pool '%s'"%(session.session_id, 
                                                                                        pool.name))
            self.taskFail(session)
            return        

        self.info("[%08X]add port resource success, %d resource(s) add to pool '%s'"%(session.session_id, 
                                                                                      resource_count, 
                                                                                      pool.name))
        
        response = getResponse(RequestDefine.add_port_resource)
        response.session = session.request_session
        response.success = True
      
        self.sendMessage(response, session.request_module)
        session.finish()

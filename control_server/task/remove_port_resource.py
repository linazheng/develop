#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from port_resource import *

class RemovePortResourceTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 port_manager):
        self.port_manager = port_manager
        logger_name = "task.remove_port_resource"
        BaseTask.__init__(self, task_type, RequestDefine.remove_port_resource,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool_id = request.getString(ParamKeyDefine.pool)
        ip_array = request.getStringArray(ParamKeyDefine.ip)
        
        if bool(ip_array):
            resource_count = len(ip_array)
        else:
            resource_count = 0
            
        self.info("[%08X]receive remove port resource request from '%s', %d resource from pool '%s'"%(
                                                                                                      session.session_id, session.request_module,
                                                                                                      resource_count, pool_id))
        if not self.port_manager.containsPool(pool_id):
            self.error("[%08X]remove port resource fail, invalid pool id '%s'"%(
                                                                                session.session_id, pool_id))
            self.taskFail(session)
            return
        
        pool = self.port_manager.getPool(pool_id)
        if ip_array == None or not pool.removeResource(ip_array):
            self.error("[%08X]remove port resource fail, can't remove resource from pool '%s'"%(
                                                                                                session.session_id, pool.name))
            self.taskFail(session)
            return             

        self.info("[%08X]remove port resource success, %d resource(s) removed from pool '%s'"% (session.session_id, resource_count, pool.name))
        
        response = getResponse(RequestDefine.remove_port_resource)
        response.session = session.request_session
        response.success = True
    
        self.sendMessage(response, session.request_module)
        session.finish()

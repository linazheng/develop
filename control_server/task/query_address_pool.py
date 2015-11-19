#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_task import *
from service.message_define import *
from address_pool import *

class QueryAddressPoolTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 address_manager):
        self.address_manager = address_manager
        logger_name = "task.query_address_pool"
        BaseTask.__init__(self, task_type, RequestDefine.query_address_pool,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        
        self.info("[%08X]receive query address pool message." % (session.session_id))
        
        request = session.initial_message
        pool_list = self.address_manager.queryAllPool()
        if 0 == len(pool_list):
            self.error("[%08X]query address pool fail, no address pool available"%
                       session.session_id)
            self.taskFail(session)
            return
        
        name = []
        uuid = []
        status = []
        count = []
        for pool in pool_list:
            name.append(pool.name)
            uuid.append(pool.uuid)
            if pool.enable:
                status.append(1)
            else:
                status.append(0)
                
            available, total = pool.statistic()
            count.append([available, total])

        self.info("[%08X]query address pool success, %d address pool(s) available"%
                  (session.session_id, len(pool_list)))
        
        response = getResponse(RequestDefine.query_address_pool)
        response.session = session.request_session
        response.success = True
        response.setStringArray(ParamKeyDefine.name, name)
        response.setStringArray(ParamKeyDefine.uuid, uuid)
        response.setUIntArray(ParamKeyDefine.status, status)
        response.setUIntArrayArray(ParamKeyDefine.count, count)
        
        self.sendMessage(response, session.request_module)
        session.finish()

#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from host_forwarder import *

class QueryForwarderSummaryTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 forwarder_manager):
        self.forwarder_manager = forwarder_manager
        logger_name = "task.query_forwarder_summary"
        BaseTask.__init__(self, task_type, RequestDefine.query_forwarder_summary,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        mono_enabled, mono_total, share_enabled, share_total = self.forwarder_manager.statistic()

        type_array = [ForwarderTypeEnum.mono,
                      ForwarderTypeEnum.share,
                      ForwarderTypeEnum.domain]

        count_array = [[mono_enabled, mono_total],
                       [share_enabled, share_total],
                       [0,0]]
                
        response = getResponse(RequestDefine.query_forwarder_summary)
        response.session = session.request_session
        response.success = True               
        response.setUIntArray(ParamKeyDefine.type, type_array)      
        response.setUIntArrayArray(ParamKeyDefine.count, count_array)                 
            
        self.info("[%08X]query forwarder summary success, %d type(s) available"%(
            session.session_id, len(type_array)))
        self.sendMessage(response, session.request_module)
        session.finish()

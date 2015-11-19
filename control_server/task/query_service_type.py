#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from service_status import *

class QueryServiceTypeTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 service_manager):
        self.service_manager = service_manager
        logger_name = "task.query_service_type"
        BaseTask.__init__(self, task_type, RequestDefine.query_service_type,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        all_type = self.service_manager.getAllServiceType()
        type_count = len(all_type)
        
        response = getResponse(RequestDefine.query_service_type)
        response.session = session.request_session
        response.success = True

        name = []
        type_array = []
        count = []
        status = []
        for service_type in all_type:
            service_list = []
            
            service_stop = 0
            service_warning = 0
            service_error = 0
            service_running = 0
            group_list = self.service_manager.queryServiceGroup(service_type)
            for service_group in group_list:
                service_list.extend(self.service_manager.queryService(service_type, service_group))

            for service in service_list:
                if service.isRunning():
                    service_running += 1
                elif ServiceStatus.status_warning == service.status:
                    service_warning += 1
                elif ServiceStatus.status_error == service.status:
                    service_error += 1
                else:
                    service_stop += 1

            name.append("default")
            type_array.append(service_type)
            count.append([service_stop, service_warning, service_error, service_running])
            if 0 != service_error:
                status.append(ServiceStatus.status_error)
            elif 0 != service_warning:
                status.append(ServiceStatus.status_warning)
            else:
                status.append(ServiceStatus.status_running)
            

        response.setStringArray(ParamKeyDefine.name, name)            
        response.setUIntArray(ParamKeyDefine.type, type_array)            
        response.setUIntArrayArray(ParamKeyDefine.count, count)                 
        response.setUIntArray(ParamKeyDefine.status, status)
            
        self.info("[%08X]query service type success, %d service type(s) available"%(
            session.session_id, type_count))
        self.sendMessage(response, session.request_module)
        session.finish()

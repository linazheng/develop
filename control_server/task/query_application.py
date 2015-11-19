#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryApplicationTask(BaseTask):
    def __init__(self, task_type, messsage_handler,
                 status_manager, iso_manager, image_manager):
        self.status_manager = status_manager
        self.iso_manager = iso_manager
        self.image_manager = image_manager
        logger_name = "task.query_application"
        BaseTask.__init__(self, task_type, RequestDefine.query_application,
                          messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        ##[stop, warn, error, running]
        host_statistic = self.status_manager.statisticHostStatus()
        disk_statistic = [0, 0, 0, 0]
        terminal_statistic = [0, 0, 0, 0]
        ##[disable, enable]
        iso_statistic = self.iso_manager.statisticStatus()
        ##[disable, enable]
        image_statistic = self.image_manager.statisticStatus()

        total_host = sum(host_statistic)
        total_disk = sum(disk_statistic)
        total_terminal = sum(terminal_statistic)
        total_iso = sum(iso_statistic)
        total_image = sum(image_statistic)
        self.info("[%08X]query application success, %d host/%d disk/%d terminal/%d iso/%d disk image"%
                  (session.session_id, total_host, total_disk,
                   total_terminal, total_iso, total_image))
        
        response = getResponse(RequestDefine.query_application)
        response.session = session.request_session
        response.success = True
        
        response.setUIntArray(ParamKeyDefine.host, host_statistic)
        response.setUIntArray(ParamKeyDefine.disk, disk_statistic)
        response.setUIntArray(ParamKeyDefine.terminal, terminal_statistic)
        response.setUIntArray(ParamKeyDefine.iso_image, iso_statistic)
        response.setUIntArray(ParamKeyDefine.disk_image, image_statistic)
        
        self.sendMessage(response, session.request_module)
        session.finish()

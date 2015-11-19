#!/usr/bin/python
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from service.message_define import ParamKeyDefine
from service.message_define import getResponse

class QueryComputePoolDetailTask(BaseTask):

    def __init__(self, task_type, message_handler, compute_pool_manager):
        self.compute_pool_manager = compute_pool_manager
        logger_name = "task.query_compute_pool_detail"
        BaseTask.__init__(self, task_type, RequestDefine.query_compute_pool_detail, message_handler, logger_name)

    def invokeSession(self, session):
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)

        if not self.compute_pool_manager.containsPool(uuid):
            self.error("[%08X] <query_compute_pool_detail> fail, invalid id '%s'" % (session.session_id, uuid))
            self.taskFail(session)
            return
        
        pool = self.compute_pool_manager.getPool(uuid)

        response = getResponse(RequestDefine.query_compute_pool_detail)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.name,        pool.name)
        response.setUInt(ParamKeyDefine.network_type,  pool.network_type)
        response.setString(ParamKeyDefine.network,     pool.network)
        response.setUInt(ParamKeyDefine.disk_type,     pool.disk_type)
        response.setString(ParamKeyDefine.disk_source, pool.disk_source)
        response.setUIntArray(ParamKeyDefine.mode,     [pool.high_available, pool.auto_qos, pool.thin_provisioning, pool.backing_image])
        response.setString(ParamKeyDefine.path,        pool.path)
        response.setString(ParamKeyDefine.crypt,       pool.crypt)

        self.info("[%08X] <query_compute_pool_detail> success, pool id '%s'" % (session.session_id, uuid))
        self.sendMessage(response, session.request_module)
        session.finish()




















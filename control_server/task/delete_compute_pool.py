#!/usr/bin/python
from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse

class DeleteComputePoolTask(BaseTask):

    def __init__(self, task_type, messsage_handler, compute_manager, status_manager):
        self.compute_manager = compute_manager
        self.status_manager = status_manager
        logger_name = "task.delete_compute_pool"
        BaseTask.__init__(self, task_type, RequestDefine.delete_compute_pool, messsage_handler, logger_name)

    def invokeSession(self, session):

        self.info("[%08X] <delete_compute_pool> receive request" %
                  (session.session_id))

        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        if not self.compute_manager.deletePool(uuid):
            self.error("[%08X] <delete_compute_pool> fail" %
                       (session.session_id))
            self.taskFail(session)
            return
        self.status_manager.removeComputePoolStatus(uuid)

        self.info("[%08X] <delete_compute_pool> success, pool '%s'" %
                  (session.session_id, uuid))

        response = getResponse(RequestDefine.delete_compute_pool)
        response.session = session.request_session
        response.success = True

        self.sendMessage(response, session.request_module)
        session.finish()

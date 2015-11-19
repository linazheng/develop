#!/usr/bin/python
from compute_resource import *
from service.message_define import *
from transaction.base_task import *

class AddComputeResourceTask(BaseTask):

    timeout = 5

    def __init__(self, task_type, messsage_handler, compute_manager, service_manager):
        self.compute_manager = compute_manager
        self.service_manager = service_manager
        logger_name = "task.add_compute_resource"
        BaseTask.__init__(self, task_type, RequestDefine.add_compute_resource, messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_success, self.onSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.modify_service, result_fail, self.onFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        pool = request.getString(ParamKeyDefine.pool)
        name = request.getString(ParamKeyDefine.name)

        self.info("[%08X] <add_compute_resource> receive request from '%s', pool id '%s', name '%s'" %
                  (session.session_id, session.request_module, pool, name))

        if not self.compute_manager.containsPool(pool):
            self.error("[%08X] <add_compute_resource> fail, invalid pool id '%s'" %
                       (session.session_id, pool))
            self.taskFail(session)
            return
        compute_pool = self.compute_manager.getPool(pool)

        if not self.service_manager.containsService(name):
            self.error("[%08X] <add_compute_resource> fail, invalid service '%s'" %
                       (session.session_id, name))
            self.taskFail(session)
            return
        service = self.service_manager.getService(name)
        
        contains, pool_id =  self.compute_manager.searchResource(name)
        if contains == True:
            another_compute_pool = self.compute_manager.getPool(pool_id)
            self.error("[%08X] <add_compute_resource> fail, resource '%s' has been allocated to compute pool '%s'('%s')" %
                       (session.session_id, name, another_compute_pool.name, another_compute_pool.uuid))
            self.taskFail(session)
            return
        
        ##status check
        if not service.isRunning():
            self.error("[%08X] <add_compute_resource> fail, invalid service status (%s/%d)" %
                       (session.session_id, service.name, service.status))
            self.taskFail(session)
            return

        if service.type != NodeTypeDefine.node_client:
            self.error("[%08X] <add_compute_resource> fail, service '%s' is not a compute node" %
                       (session.session_id, name))
            self.taskFail(session)
            return

        config = ComputeResource()
        config.name = name
        config.server = service.server

        if compute_pool.disk_type == service.disk_type:
            if not self.compute_manager.addResource(pool, [config]):
                self.error("[%08X] <add_compute_resource> fail" %
                           (session.session_id))
                self.taskFail(session)
                return

            self.info("[%08X] <add_compute_resource> success" %
                      (session.session_id))

            response = getResponse(RequestDefine.add_compute_resource)
            response.session = session.request_session
            response.success = True

            self.sendMessage(response, session.request_module)
            session.finish()
        else:
            self.info("[%08X] <add_compute_resource> request modify service, service '%s', disk type '%d'" %
                      (session.session_id, name, compute_pool.disk_type))
            modify_request = getRequest(RequestDefine.modify_service)
            modify_request.session = session.session_id
            modify_request.setUInt(ParamKeyDefine.disk_type, compute_pool.disk_type)
            modify_request.setString(ParamKeyDefine.disk_source, compute_pool.path)
            modify_request.setString(ParamKeyDefine.crypt, compute_pool.crypt)

            self.sendMessage(modify_request, name)
            self.setTimer(session, self.timeout)

            session.pool = pool
            session.config = config
            session.compute_pool = compute_pool

    def onSuccess(self, msg, session):
        self.clearTimer(session)

        self.info("[%08X] <add_compute_resource> modify service success" %
                  (session.session_id))
        service = self.service_manager.getService(session.config.name)
        if service != None:
            service.disk_type = session.compute_pool.disk_type

        if not self.compute_manager.addResource(session.pool, [session.config]):
            self.error("[%08X] <add_compute_resource> fail" %
                       (session.session_id))
            self.taskFail(session)
            return

        self.info("[%08X] <add_compute_resource> success" %
                  (session.session_id))

        response = getResponse(RequestDefine.add_compute_resource)
        response.session = session.request_session
        response.success = True

        self.sendMessage(response, session.request_module)
        session.finish()

    def onFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <add_compute_resource> fail, modify service fail" %
                   (session.session_id))
        self.taskFail(session)

    def onTimeout(self, msg, session):
        self.error("[%08X] <add_compute_resource> fail, modify service timeout" %
                   (session.session_id))
        self.taskFail(session)

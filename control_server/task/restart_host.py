#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum
from service.message_define import *
from transaction.base_task import *

class RestartHostTask(BaseTask):

    operate_timeout = 5

    def __init__(self, task_type, messsage_handler, config_manager, iso_manager, service_manager):
        self.config_manager = config_manager
        self.iso_manager = iso_manager
        self.service_manager = service_manager
        logger_name = "task.restart_host"
        BaseTask.__init__(self, task_type, RequestDefine.restart_host, messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.restart_host, result_success, self.onStartSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.restart_host, result_fail, self.onStartFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onStartTimeout)

    def invokeSession(self, session):
        """
        task restart, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        boot = request.getUInt(ParamKeyDefine.boot)
        image_id = request.getString(ParamKeyDefine.image)

        self.info("[%08X] <restart_host> receive request from '%s', host id '%s', boot '%d'" %
                       (session.session_id, session.request_module, uuid, boot))

        if not self.config_manager.containsHost(uuid):
            self.error("[%08X] <restart_host> fail, invalid host id '%s'" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        host = self.config_manager.getHost(uuid)
        node_client_name = host.container

        if not self.service_manager.containsService(node_client_name):
            self.error("[%08X] <restart_host> fail, host container '%s' does not exist" %
                       (session.session_id, node_client_name))
            self.taskFail(session)
            return
        node_client = self.service_manager.getService(node_client_name)

        if 1 == boot:
            # #boot from iso
            if not self.iso_manager.containsImage(image_id):
                self.error("[%08X] <restart_host> fail, invalid boot iso '%s'" %
                       (session.session_id, image_id))
                self.taskFail(session)
                return
            image = self.iso_manager.getImage(image_id)

            if image.disk_type != node_client.disk_type:
                self.error("[%08X] <restart_host> fail, disk type not match, iso image '%s/%d', node client '%s/%d'" %
                           (session.session_id, image.name, image.disk_type, node_client.name, node_client.disk_type))
                self.taskFail(session)
                return

            request.setUInt(ParamKeyDefine.disk_type, image.disk_type)

            if image.disk_type == ComputeStorageTypeEnum.local:
                self.info("[%08X] <restart_host> boot from iso '%s', address '%s:%d'" %
                           (session.session_id, image.name, image.ip, image.port))
                request.setString(ParamKeyDefine.image, image.name)
                request.setString(ParamKeyDefine.ip, image.ip)
                request.setUInt(ParamKeyDefine.port, image.port)
            elif image.disk_type == ComputeStorageTypeEnum.nas:
                self.info("[%08X] <restart_host> boot from iso '%s', path '%s'" %
                           (session.session_id, image.name, image.path))
                request.setString(ParamKeyDefine.path, image.path)

        self.info("[%08X] <restart_host> redirect restart host '%s'('%s') to compute node '%s'" %
                       (session.session_id, host.name, host.uuid, node_client_name))
        session.target = uuid
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, node_client_name)

    def onStartSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <restart_host> success, id '%s'" %
                       (session.session_id, session.target))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onStartFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <restart_host> fail, id '%s'" %
                  (session.session_id, session.target))
        self.taskFail(session)

    def onStartTimeout(self, msg, session):
        self.info("[%08X] <restart_host> timeout, id '%s'" %
                  (session.session_id, session.target))
        self.taskFail(session)


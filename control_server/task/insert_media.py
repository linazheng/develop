#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum
from service.message_define import *
from transaction.base_task import *

class InsertMediaTask(BaseTask):

    operate_timeout = 5

    def __init__(self, task_type, messsage_handler, config_manager, iso_manager, service_manager):
        self.config_manager = config_manager
        self.iso_manager = iso_manager
        self.service_manager = service_manager
        logger_name = "task.insert_media"
        BaseTask.__init__(self, task_type, RequestDefine.insert_media, messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.insert_media, result_success, self.onInsertSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.insert_media, result_fail, self.onInsertFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onInsertTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        image_id = request.getString(ParamKeyDefine.image)

        self.info("[%08X] <insert_media> receive request from '%s', host id '%s'" %
                       (session.session_id, session.request_module, uuid))

        if not self.config_manager.containsHost(uuid):
            self.error("[%08X] <insert_media> fail, invalid host id '%s'" %
                       (session.session_id, uuid))
            self.taskFail(session)
            return
        host = self.config_manager.getHost(uuid)
        node_client_name = host.container

        if not self.service_manager.containsService(node_client_name):
            self.error("[%08X] <insert_media> fail, host container '%s' does not exist" %
                       (session.session_id, node_client_name))
            self.taskFail(session)
            return
        node_client = self.service_manager.getService(node_client_name)

        if not self.iso_manager.containsImage(image_id):
            self.error("[%08X] <insert_media> fail, invalid iso id '%s'" %
                   (session.session_id, image_id))
            self.taskFail(session)
            return
        image = self.iso_manager.getImage(image_id)

        if image.disk_type != node_client.disk_type:
            self.error("[%08X] <insert_media> fail, disk type not match, iso image '%s/%d', node client '%s/%d'" %
                       (session.session_id, image.name, image.disk_type, node_client.name, node_client.disk_type))
            self.taskFail(session)
            return

        request.setUInt(ParamKeyDefine.disk_type, image.disk_type)

        if image.disk_type == ComputeStorageTypeEnum.local:  # #image name, ip, port
            self.info("[%08X] <insert_media> insert iso media '%s' into host '%s', address '%s:%d'" %
                   (session.session_id, image.name, host.name, image.ip, image.port))
            request.setString(ParamKeyDefine.image, image.name)
            request.setString(ParamKeyDefine.ip, image.ip)
            request.setUInt(ParamKeyDefine.port, image.port)
        elif image.disk_type == ComputeStorageTypeEnum.nas:  # # image path
            self.info("[%08X] <insert_media> insert iso media '%s' into host '%s', path '%s'" %
                       (session.session_id, image.name, host.name, image.path))
            request.setString(ParamKeyDefine.path, image.path)

        self.info("[%08X] <insert_media> redirect insert media '%s'('%s') to compute node '%s'" %
                       (session.session_id, image.name, image.uuid, node_client_name))
        session.target = image_id
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, node_client_name)

    def onInsertSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <insert_media> success, iso id '%s'" %
                       (session.session_id, session.target))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()

    def onInsertFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <insert_media> fail, iso id '%s'" %
                  (session.session_id, session.target))
        self.taskFail(session)

    def onInsertTimeout(self, msg, session):
        self.info("[%08X] <insert_media> timeout, iso id '%s'" %
                  (session.session_id, session.target))
        self.taskFail(session)


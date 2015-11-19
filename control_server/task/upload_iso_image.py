#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from iso_image import *

class UploadISOImageTask(BaseTask):

    operate_timeout = 5

    def __init__(self, task_type, messsage_handler, iso_manager):
        self.iso_manager = iso_manager
        logger_name = "task.upload_iso_image"
        BaseTask.__init__(self, task_type, RequestDefine.upload_iso_image, messsage_handler, logger_name)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.upload_iso_image, result_success, self.onUploadSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.upload_iso_image, result_fail, self.onUploadFail)
        self.addTransferRule(state_initial, AppMessage.EVENT, EventDefine.timeout, result_any, self.onUploadTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        name = request.getString(ParamKeyDefine.name)
        target = request.getString(ParamKeyDefine.target)

        self.info("[%08X] <upload_iso_image> receive request from '%s', image '%s', target '%s'" %
                  (session.session_id, session.request_module, name, target))

        if self.iso_manager.containsImageName(name):
            self.error("[%08X] <upload_iso_image> fail, image '%s' already exists" %
                       (session.session_id, name))
            self.taskFail(session)
            return

        # #select default storage server
        session.target = self.message_handler.getStorageServer()
        self.info("[%08X]redirect upload request to service '%s'..." %
                  (session.session_id, session.target))

        request.session = session.session_id
        self.sendMessage(request, session.target)
        self.setTimer(session, self.operate_timeout)

    def onUploadFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <upload_iso_image> fail" %
                   (session.session_id))
        self.taskFail(session)

    def onUploadTimeout(self, msg, session):
        self.error("[%08X] <upload_iso_image> timeout" %
                   (session.session_id))
        self.taskFail(session)

    def onUploadSuccess(self, msg, session):
        self.clearTimer(session)
        request = session.initial_message
        image = ISOImage()
        image.name = request.getString(ParamKeyDefine.name)
        image.description = request.getString(ParamKeyDefine.description)
        image.group = request.getString(ParamKeyDefine.group)
        image.user = request.getString(ParamKeyDefine.user)
        image.disk_type = request.getUInt(ParamKeyDefine.disk_type)
        # #response msg
        image.uuid = msg.getString(ParamKeyDefine.uuid)
        image.ip = msg.getString(ParamKeyDefine.ip)
        image.port = msg.getUInt(ParamKeyDefine.port)
        image.size = msg.getUInt(ParamKeyDefine.size)

        if image.disk_type == ComputeStorageTypeEnum.nas:
            # # path : iso_image/{group_name}/{image_id}.iso
            path = "iso_image/%s/%s.iso" % (image.group, image.uuid)
            image.path = path
        image.container = session.target

        if not self.iso_manager.addImage(image):
            self.error("[%08X] <upload_iso_image> success, but can't add image '%s'('%s')" %
                       (session.session_id, image.name, image.uuid))
            self.taskFail(session)
            return

        self.info("[%08X] <upload_iso_image> success, image '%s'('%s'), size %.f MiB, address '%s:%d'" %
                  (session.session_id, image.name, image.uuid, float(image.size) / 1048576, image.ip, image.port))

        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)


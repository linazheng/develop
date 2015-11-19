#!/usr/bin/python
from transaction.base_task import *
from transaction.state_define import *
from service.message_define import *
from iso_image import *
from disk_image import *
import os

class InitialStorageTask(BaseTask):
    query_timeout = 5
    def __init__(self, task_type, messsage_handler,
                 iso_manager, service_manager, image_manager):
        self.iso_manager = iso_manager
        self.service_manager = service_manager
        self.image_manager = image_manager
        logger_name = "task.initial_storage"
        BaseTask.__init__(self, task_type, RequestDefine.invalid,
                          messsage_handler, logger_name)

        # #state rule define, state id from 1
        stQueryImage = 2
        stQueryWhisper = 3
        self.addState(stQueryImage)
        self.addState(stQueryWhisper)

        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_iso_image, result_success, self.onQueryISOSuccess, stQueryImage)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_iso_image, result_fail,    self.onQueryISOFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,           result_any,     self.onQueryISOTimeout)

        self.addTransferRule(stQueryImage, AppMessage.RESPONSE, RequestDefine.query_disk_image, result_success, self.onQueryImageSuccess)
        self.addTransferRule(stQueryImage, AppMessage.RESPONSE, RequestDefine.query_disk_image, result_fail,    self.onQueryImageFail)
        self.addTransferRule(stQueryImage, AppMessage.EVENT,    EventDefine.timeout,            result_any,     self.onQueryImageTimeout)

    def invokeSession(self, session):
        """
        task start, must override
        """
        self.info("[%08X] <initial_storage> start to initial storage" %
                  (session.session_id))
        session.target = session.initial_message.getString(ParamKeyDefine.target)
        request = getRequest(RequestDefine.query_iso_image)
        request.session = session.session_id
        self.info("[%08X] <initial_storage> query iso images to '%s'..." % (
            session.session_id, session.target))

        self.sendMessage(request, session.target)
        self.setTimer(session, self.query_timeout)

    # self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.query_iso_image, result_success, self.onQueryISOSuccess, stQueryImage)
    def onQueryISOSuccess(self, response, session):
        self.clearTimer(session)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        count = len(uuid)
        if 0 == count:
            # #clear all
            self.iso_manager.loadImages(session.target, [])
            self.info("[%08X] <initial_storage> query iso images success, but no image available in storage server '%s'" %
                  (session.session_id, session.target))
        else:
            name = response.getStringArray(ParamKeyDefine.name)
            status = response.getUIntArray(ParamKeyDefine.status)
            size = response.getUIntArray(ParamKeyDefine.size)
            description = response.getStringArray(ParamKeyDefine.description)
            ip = response.getStringArray(ParamKeyDefine.ip)
            port = response.getUIntArray(ParamKeyDefine.port)
            group = response.getStringArray(ParamKeyDefine.group)
            user = response.getStringArray(ParamKeyDefine.user)
            path = response.getStringArray(ParamKeyDefine.path)
            disk_type = response.getUIntArray(ParamKeyDefine.disk_type)
            image_list = []
            for i in range(count):
                image = ISOImage()
                image.name = name[i]
                image.uuid = uuid[i]
                if 1 == status[i]:
                    # #disable
                    image.enabled = False
                else:
                    image.enabled = True
                image.size = size[i]
                image.description = description[i]
                image.ip = ip[i]
                image.port = port[i]
                image.group = group[i]
                image.user = user[i]
                
                if path != None:
                    image.path = path[i]
                    
                if disk_type != None:
                    image.disk_type = disk_type[i]
                    
                image.container = session.target
                image_list.append(image)

            if not self.iso_manager.loadImages(session.target, image_list):
                self.error("[%08X] <initial_storage> query iso images success, but load images fail" %
                      (session.session_id))
                session.finish()
                return

            self.info("[%08X] <initial_storage> query iso images success, %d image(s) in storage server '%s'" %
                      (session.session_id, count, session.target))

        request = getRequest(RequestDefine.query_disk_image)
        request.session = session.session_id
        self.info("[%08X] <initial_storage> query disk image in '%s'..." % (
            session.session_id, session.target))

        self.sendMessage(request, session.target)
        self.setTimer(session, self.query_timeout)

    def onQueryISOFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X] <initial_storage> query images fail" % session.session_id)
        session.finish()

    def onQueryISOTimeout(self, response, session):
        self.info("[%08X] <initial_storage> query images timeout" % session.session_id)
        session.finish()

    # self.addTransferRule(stQueryImage, AppMessage.RESPONSE, RequestDefine.query_disk_image, result_success, self.onQueryImageSuccess)
    def onQueryImageSuccess(self, response, session):
        self.clearTimer(session)
        uuid = response.getStringArray(ParamKeyDefine.uuid)
        count = len(uuid)
        if 0 == count:
            # #clear all
            self.image_manager.loadImages(session.target, [])
            self.info("[%08X] <initial_storage> query disk images success, but no image available in storage server '%s'" %
                  (session.session_id, session.target))
        else:
            name        = response.getStringArray(ParamKeyDefine.name)
            status      = response.getUIntArray(ParamKeyDefine.status)
            size        = response.getUIntArray(ParamKeyDefine.size)
            description = response.getStringArray(ParamKeyDefine.description)
            identity    = response.getStringArrayArray(ParamKeyDefine.identity)
            group       = response.getStringArray(ParamKeyDefine.group)
            user        = response.getStringArray(ParamKeyDefine.user)
            path        = response.getStringArray(ParamKeyDefine.path)
            disk_type   = response.getUIntArray(ParamKeyDefine.disk_type)
            file_type = response.getUIntArray(ParamKeyDefine.file_type)
            
            image_list = []
            for i in range(count):
                image = DiskImage()
                image.name = name[i]
                image.uuid = uuid[i]
                if 1 == status[i]:
                    # #disable
                    image.enabled = False
                else:
                    image.enabled = True
                image.size = size[i]
                image.description = description[i]
                image.tags = identity[i]
                image.group = group[i]
                image.user = user[i]
                if path != None:
                    image.path = path[i]

                if disk_type != None:
                    image.disk_type = disk_type[i]
                
                if file_type != None:
                    image.file_type = file_type[i]

                image.container = session.target
                image_list.append(image)

            if not self.image_manager.loadImages(session.target, image_list):
                self.error("[%08X] <initial_storage> query disk images success, but load images fail" % (session.session_id))
                session.finish()
                return

            self.info("[%08X] <initial_storage> query disk images success, %d image(s) in storage server '%s'" % (session.session_id, count, session.target))

        session.finish()

    def onQueryImageFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X] <initial_storage> query images fail" % session.session_id)
        session.finish()

    def onQueryImageTimeout(self, response, session):
        self.info("[%08X] <initial_storage> query images timeout" % session.session_id)
        session.finish()


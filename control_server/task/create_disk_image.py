#!/usr/bin/python
from disk_image import *
from service.message_define import *
from transaction.base_task import *
from compute_pool import ThinProvisioningModeEnum

class CreateDiskImageTask(BaseTask):

    operate_timeout = 5
    max_timeout = 3

    def __init__(self, task_type, messsage_handler,
                 config_manager, service_manager, image_manager):
        self.config_manager = config_manager
        self.service_manager = service_manager
        self.image_manager = image_manager
        logger_name = "task.create_disk_image"
        BaseTask.__init__(self, task_type, RequestDefine.create_disk_image,
                          messsage_handler, logger_name)

        # #state rule define, state id from 1
        state_nc_transport = 1
        state_ss_creating = 2
        self.addState(state_nc_transport)
        self.addState(state_ss_creating)

        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.ack,                 result_success, self.onStartSuccess, state_nc_transport)
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_fail,    self.onStartFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onStartTimeout)

        self.addTransferRule(state_nc_transport, AppMessage.EVENT,    EventDefine.report,              result_success, self.onTransportProgress, state_nc_transport)
        self.addTransferRule(state_nc_transport, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onTransportTimeout,  state_nc_transport)
        self.addTransferRule(state_nc_transport, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_success, self.onTransportSuccess,  state_ss_creating)
        self.addTransferRule(state_nc_transport, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_fail,    self.onTransportFail)

        self.addTransferRule(state_ss_creating, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_success, self.onCreateSuccess)
        self.addTransferRule(state_ss_creating, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_fail,    self.onCreateFail)
        self.addTransferRule(state_ss_creating, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onCreateTimeout)


    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        
        session._ext_data = {}
        
        image_name = request.getString(ParamKeyDefine.name)
        uuid       = request.getString(ParamKeyDefine.uuid)
        
        self.info("[%08X] <create_disk_image> receive request from '%s', image '%s', target host '%s'" %
                  (session.session_id, session.request_module, image_name, uuid))

        if self.image_manager.containsImageName(image_name):
            self.error("[%08X] <create_disk_image> fail, image '%s' already exists" % (
                session.session_id, image_name))
            self.taskFail(session)
            return

        if not self.config_manager.containsHost(uuid):
            self.error("[%08X] <create_disk_image> fail, invalid host id '%s'" % (
                session.session_id, uuid))
            self.taskFail(session)
            return
        
        host = self.config_manager.getHost(uuid)
        node_client_name = host.container
        
        session._ext_data["host"] = host; 
        
        # judge the disk_type of node_client and storage_server is the same or not
        if not self.service_manager.containsService(node_client_name):
            self.error("[%08X] <create_disk_image> fail, invalid node client '%s'" %
                       (session.session_id, node_client_name))
            self.taskFail(session)
            return
        
        node_client = self.service_manager.getService(node_client_name)

        # #select default storage_server
        storage_server_name = self.message_handler.getStorageServer()
        if not self.service_manager.containsService(storage_server_name):
            self.error("[%08X] <create_disk_image> fail, invalid storage server '%s'" %
                       (session.session_id, node_client_name))
            self.taskFail(session)
            return
        storage_server = self.service_manager.getService(storage_server_name)

        if node_client.disk_type != storage_server.disk_type:
            self.error("[%08X] <create_disk_image> fail, disk type not match, node_client '%s/%d', storage_server '%s/%d'" %
                       (session.session_id, node_client.name, node_client.disk_type, storage_server.name, storage_server.disk_type))
            self.taskFail(session)
            return

        request.setUInt(ParamKeyDefine.disk_type, node_client.disk_type)
        session.storage_server = storage_server_name
        session.disk_type = node_client.disk_type

        if node_client.disk_type == ComputeStorageTypeEnum.local:
            
            # #get whishper
            if not self.service_manager.containsWhisper(storage_server_name):
                self.error("[%08X] <create_disk_image> fail, no whisper serivce in '%s'" % (
                    session.session_id, storage_server_name))
                self.taskFail(session)
                return
            whisper = self.service_manager.getWhisper(storage_server_name)

            ip = whisper.ip
            port = whisper.port
            self.info("[%08X] <create_disk_image> node client '%s', storage service '%s'('%s:%d')" % (
                    session.session_id, node_client_name, storage_server_name, ip, port))
            request.setString(ParamKeyDefine.target, storage_server_name)
            request.setString(ParamKeyDefine.ip, ip)
            request.setUInt(ParamKeyDefine.port, port)
            request.session = session.session_id

            self.info("[%08X] <create_disk_image> disk type '%d', redirect to '%s'..." % (
                    session.session_id, node_client.disk_type, node_client_name))

            self.sendMessage(request, node_client_name)
            self.setTimer(session, self.operate_timeout)
            
        elif node_client.disk_type == ComputeStorageTypeEnum.nas:
            
            group = request.getString(ParamKeyDefine.group)
            ## path : disk_image/{group_name}
            path = "disk_image/%s" % (group)
            request.setString(ParamKeyDefine.target, path)
            request.session = session.session_id

            session.path = path

            self.info("[%08X] <create_disk_image> disk type '%d', redirect to '%s'..." % (
                    session.session_id, node_client.disk_type, node_client_name))

            self.sendMessage(request, node_client_name)
            self.setTimer(session, self.operate_timeout)
            
        else:
            
            self.error("[%08X] <create_disk_image> fail, not support disk type '%d'" %
                       (session.session_id, node_client.disk_type))
            self.taskFail(session)
            return


    # self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.ack,                 result_success, self.onStartSuccess, state_nc_transport)
    def onStartSuccess(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X] <create_disk_image> started" %
                       (session.session_id))
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        self.setTimer(session, self.operate_timeout)

    # self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_fail,    self.onStartFail)
    def onStartFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <create_disk_image> start fail" %
                  (session.session_id))
        self.taskFail(session)

    # self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,             result_any,     self.onStartTimeout)
    def onStartTimeout(self, msg, session):
        self.error("[%08X] <create_disk_image> start timeout" %
                  (session.session_id))
        self.taskFail(session)

    #-----------------------

    #
    def onTransportProgress(self, msg, session):
        self.clearTimer(session)
        session.counter = 0
        level = msg.getUInt(ParamKeyDefine.level)
        self.info("[%08X] <create_disk_image> transport on progess, %d %%" %
                  (session.session_id, level))
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        self.setTimer(session, self.operate_timeout)

    def onTransportTimeout(self, msg, session):
        session.counter += 1
        if session.counter >= self.max_timeout:
            self.error("[%08X] <create_disk_image> remote service transport data exceed max timeout( %d/ %d)" % (
                session.session_id, session.counter, self.max_timeout))
            self.taskFail(session)
        else:
            self.warn("[%08X] <create_disk_image> remote service transport data timeout( %d/ %d)" % (
                session.session_id, session.counter, self.max_timeout))
            self.setTimer(session, self.operate_timeout)


    # self.addTransferRule(state_nc_transport, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_success, self.onTransportSuccess,  state_ss_creating)
    def onTransportSuccess(self, msg, session):
        self.clearTimer(session)
        
        host = session._ext_data["host"]
        
        uuid = msg.getString(ParamKeyDefine.uuid)
        size = msg.getUInt(ParamKeyDefine.size)

        if session.disk_type == ComputeStorageTypeEnum.local:
            
            request = session.initial_message
            
            image = DiskImage()
            image.name        = request.getString(ParamKeyDefine.name)
            image.description = request.getString(ParamKeyDefine.description)
            image.tags        = request.getStringArray(ParamKeyDefine.identity)
            image.group       = request.getString(ParamKeyDefine.group)
            image.user        = request.getString(ParamKeyDefine.user)
            image.uuid        = uuid
            image.size        = size
            image.container   = session.storage_server
            
            if host.thin_provisioning == ThinProvisioningModeEnum.enabled:
                image.file_type = DiskImageFileTypeEnum.qcow2
            else:
                image.file_type = DiskImageFileTypeEnum.raw
            
            if not self.image_manager.addImage(image):
                self.error("[%08X] <create_disk_image> success, but can't add image '%s'('%s')" % (
                    session.session_id, image.name, image.uuid))
                self.taskFail(session)
                return
            
            self.info("[%08X] <create_disk_image> success, name '%s'('%s'), size %d bytes" %
                      (session.session_id, image.name, image.uuid, size))

            msg.session = session.request_session
            self.sendMessage(msg, session.request_module)
            session.finish()
            
        elif session.disk_type == ComputeStorageTypeEnum.nas:
            if host.thin_provisioning == ThinProvisioningModeEnum.enabled:
                file_type = DiskImageFileTypeEnum.qcow2
                # # target : disk_image/{group_name}/{uuid}.qcow2
                target = "%s/%s.qcow2" % (session.path, uuid)
            else:
                file_type = DiskImageFileTypeEnum.raw
                # # target : disk_image/{group_name}/{uuid}.img
                target = "%s/%s.img" % (session.path, uuid)
            
            request = session.initial_message
            request.setString(ParamKeyDefine.target, target)
            # request.setUInt(ParamKeyDefine.disk_type, session.disk_type)
            request.setString(ParamKeyDefine.uuid,    uuid)
            request.setUInt(ParamKeyDefine.size, size)
            request.setUInt(ParamKeyDefine.file_type, file_type)

            session.size = size
            session.file_type = file_type
            session.path = target

            self.info("[%08X] <create_disk_image> transport success, redirect to '%s'..." %
                      (session.session_id, session.storage_server))

            self.sendMessage(request, session.storage_server)
            self.setTimer(session, self.operate_timeout)
            
        else:
            
            self.error("[%08X] <create_disk_image> fail, invalid disk type '%d'" %
                       (session.session_id, session.disk_type))
            self.taskFail(session)
            return


    def onTransportFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <create_disk_image> remote service transport data fail" %
                  (session.session_id))
        self.taskFail(session)

    # self.addTransferRule(state_ss_creating, AppMessage.RESPONSE, RequestDefine.create_disk_image, result_success, self.onCreateSuccess)
    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        
        uuid = msg.getString(ParamKeyDefine.uuid)

        request = session.initial_message
        image = DiskImage()
        image.name = request.getString(ParamKeyDefine.name)
        image.description = request.getString(ParamKeyDefine.description)
        image.tags = request.getStringArray(ParamKeyDefine.identity)
        image.group = request.getString(ParamKeyDefine.group)
        image.user = request.getString(ParamKeyDefine.user)
        image.uuid = uuid
        image.size = session.size
        image.path = session.path  # # path : disk_image/{group_name}/{image_id}.img|qcow2
        image.disk_type = session.disk_type
        image.container = session.storage_server
        image.file_type = session.file_type
        
        if not self.image_manager.addImage(image):
            self.error("[%08X] <create_disk_image> success, but cann't add image '%s'('%s')" % (session.session_id, image.name, image.uuid))
            self.taskFail(session)
            return
        
        self.info("[%08X] <create_disk_image> success, name '%s'('%s'), size %d bytes" % (session.session_id, image.name, image.uuid, image.size))

        msg.setUInt(ParamKeyDefine.size, session.size)
        msg.session = session.request_session
        self.sendMessage(msg, session.request_module)
        session.finish()


    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.error("[%08X] <create_disk_image> create fail" %
                   (session.session_id))
        self.taskFail(session)
        session.finish()

    def onCreateTimeout(self, msg, session):
        self.error("[%08X] <create_disk_image> create timeout" %
                   (session.session_id))
        self.taskFail(session)
        session.finish()


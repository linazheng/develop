#!/usr/bin/python
import logging
import threading
from disk_image import *

class ImageManager(object):
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        # #key = uuid, value = disk image
        self.images = {}
        # #key = image name, value = uuid
        self.image_names = {}
        # #key = service name, value = list of image uuid
        self.image_containers = {}
        self.lock = threading.RLock()

    def loadImages(self, container_name, image_list):
        with self.lock:
            if self.image_containers.has_key(container_name):
                for uuid in self.image_containers[container_name]:
                    # #remove exists
                    if self.images.has_key(uuid):
                        image = self.images[uuid]
                        if self.image_names.has_key(image.name):
                            del self.image_names[image.name]
                        del self.images[uuid]
                del self.image_containers[container_name]

            id_list = []
            for image in image_list:
                id_list.append(image.uuid)
                self.images[image.uuid] = image
                self.image_names[image.name] = image.uuid
            self.image_containers[container_name] = id_list
            self.logger.info("<DiskManager>%d disk image(s) loaded in container '%s'" % (
                len(id_list), container_name))
            return True

    def containsImage(self, uuid):
        with self.lock:
            return self.images.has_key(uuid)

    def containsImageName(self, name):
        with self.lock:
            return self.image_names.has_key(name)

    def getImage(self, uuid):
        with self.lock:
            if self.images.has_key(uuid):
                return self.images[uuid]
            else:
                return None

    def getAllImages(self):
        with self.lock:
            return self.images.values()

    def statisticStatus(self):
        with self.lock:
            disable = 0
            enable = 0
            for image in self.images.values():
                if image.enabled:
                    enable += 1
                else:
                    disable += 1

            return [disable, enable]

    def addImage(self, image):
        with self.lock:
            if self.image_names.has_key(image.name):
                self.logger.error("<image_manager> add disk image fail, image name '%s' already exists" % (
                    image.name))
                return False
            if self.images.has_key(image.uuid):
                self.logger.error("<image_manager> add disk image fail, image id '%s' already exists" % (
                    image.uuid))
                return False
            self.images[image.uuid] = image
            self.image_names[image.name] = image.uuid
            if self.image_containers.has_key(image.container):
                self.image_containers[image.container].append(image.uuid)
            else:
                self.image_containers[image.container] = [image.uuid]

            self.logger.info("<image_manager> add disk image success, name '%s'('%s'), container '%s'" % (
                image.name, image.uuid, image.container))
            return True

    def removeImage(self, uuid):
        with self.lock:
            if not self.images.has_key(uuid):
                self.logger.error("<image_manager> remove disk image fail, image '%s' not exists" % (
                    uuid))
                return False
            image = self.images[uuid]
            image_name = image.name
            container_name = image.container
            if self.image_containers.has_key(container_name):
                id_list = self.image_containers[container_name]
                if uuid in id_list:
                    del id_list[id_list.index(uuid)]
                    self.logger.info("<image_manager> remove disk image '%s' from container '%s'" % (
                        uuid, container_name))
            self.logger.info("<image_manager> remove disk image success, name '%s'('%s'), container '%s'" % (
                image_name, image.uuid, container_name))

            if self.image_names.has_key(image_name):
                del self.image_names[image_name]
            del self.images[uuid]
            return True

    def modifyImage(self, uuid, new_image):
        with self.lock:
            if not self.images.has_key(uuid):
                self.logger.error("<image_manager> modify disk image fail, image '%s' not exists" % (
                    uuid))
                return False
            image = self.images[uuid]
            if image.name != new_image.name:
                if self.image_names.has_key(image.name):
                    del self.image_names[image.name]
                self.image_names[new_image.name] = image.uuid
                image.name = new_image.name
            image.description = new_image.description
            self.logger.info("<image_manager> modify disk image success, name '%s'('%s')" % (
                image.name, image.uuid))
            return True

    def removeAllImageInContainer(self, container_name):
        self.logger.info("<image_manager> remove all images in container '%s'" %
                         (container_name))
        
        if self.image_containers.has_key(container_name):
            for uuid in self.image_containers[container_name]:
                # #remove exists
                if self.images.has_key(uuid):
                    image = self.images[uuid]
                    if self.image_names.has_key(image.name):
                        del self.image_names[image.name]
                    del self.images[uuid]
            del self.image_containers[container_name]
            return True
        
        return False


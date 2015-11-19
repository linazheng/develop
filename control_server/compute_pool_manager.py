#!/usr/bin/python
import logging
import uuid
import os.path
import io
import shutil
import threading
from ConfigParser import *
from compute_pool import *
from compute_resource import *
from resource_status_enum import *
from pool_status_enum import *
from string import strip

class ComputePoolManager(object):
    def __init__(self, resource_path, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.pool_path = os.path.join(resource_path, "compute")

        if not os.path.exists(self.pool_path):
            os.mkdir(self.pool_path)

        # #key = uuid, value = compute Pool
        self.compute_pool = {}
        # #uuid for default pool
        self.default_pool = ""
        self.lock = threading.RLock()

    def load(self):
        with self.lock:
            if not self.loadAllPool():
                # #add default pool
                pool = ComputePool()
                pool.name = "default"
                pool.status = PoolStatusEnum.running
                if not self.createPool(pool):
                    self.logger.error("<compute_pool_manager> create default pool fail")
                    return False
                self.default_pool = pool.uuid
                self.logger.info("<compute_pool_manager> create default pool success, pool '%s'('%s')" % (
                    pool.name, pool.uuid))
                return True
            elif 0 != len(self.compute_pool):
                self.default_pool = self.compute_pool.keys()[0]
            return True

    def getDefaultPoolID(self):
        with self.lock:
            return self.default_pool

    def getDefaultPool(self):
        with self.lock:
            if self.compute_pool.has_key(self.default_pool):
                return self.compute_pool[self.default_pool]
            else:
                return None

    def loadAllPool(self):
        with self.lock:
            list_file = os.path.join(self.pool_path, "compute_pool.info")
            if not os.path.exists(list_file):
                return False
            self.compute_pool = {}
            parser = ConfigParser()

            # read 'compute_pool.info'
            parser.read(list_file)
            pool_count = parser.getint("DEFAULT", "data_count")
            pool_id_list = []
            for index in range(pool_count):
                pool_id_list.append(parser.get("DEFAULT", "uuid_%d" % (index)))

            for pool_id in pool_id_list:
                path = os.path.join(self.pool_path, pool_id)
                info_file = os.path.join(path, "pool.info")
                if not os.path.exists(info_file):
                    continue

                # read '/var/zhicloud/config/control_server/resource/compute/{compute_pool_uuid}/pool.ini'
                parser.read(info_file)

                pool = ComputePool()
                pool.name = parser.get("DEFAULT", "name")
                pool.uuid = parser.get("DEFAULT", "uuid")
                pool.status = parser.getint("DEFAULT", "status")
                pool.network = parser.get("DEFAULT", "network")
                pool.network_type = parser.getint("DEFAULT", "network_type")
                pool.disk_type = parser.getint("DEFAULT", "disk_type")
                pool.disk_source = parser.get("DEFAULT", "disk_source")

                if parser.has_option("DEFAULT", "high_available"):
                    pool.high_available = parser.getint("DEFAULT", "high_available")

                if parser.has_option("DEFAULT", "auto_qos"):
                    pool.auto_qos = parser.getint("DEFAULT", "auto_qos")

                if parser.has_option("DEFAULT", "path"):
                    pool.path = parser.get("DEFAULT", "path")

                if parser.has_option("DEFAULT", "crypt"):
                    pool.crypt = parser.get("DEFAULT", "crypt")

                if parser.has_option("DEFAULT", "thin_provisioning"):
                    pool.thin_provisioning = parser.getint("DEFAULT", "thin_provisioning")

                if parser.has_option("DEFAULT", "backing_image"):
                    pool.backing_image = parser.getint("DEFAULT", "backing_image")

                resource_count = parser.getint("DEFAULT", "resource_count")
                if 0 != resource_count:
                    resource_list = []
                    for index in range(resource_count):
                        resource_list.append(parser.get("DEFAULT", "resource_%d" % (index)))

                    for resource_name in resource_list:
                        resource_file = os.path.join(path, "resource_%s.info" % (resource_name))

                        # read '/var/zhicloud/config/control_server/resource/compute/resource_{node_name}.ini'
                        parser.read(resource_file)
                        resource = ComputeResource()
                        resource.name = parser.get("DEFAULT", "name")
                        resource.server = parser.get("DEFAULT", "server")
                        resource.status = parser.getint("DEFAULT", "status")
                        host_count = parser.getint("DEFAULT", "host_count")
                        if 0 != host_count:
                            for index in range(host_count):
                                host_id = parser.get("DEFAULT", "host_%d" % (index))
                                resource.allocated.add(host_id)

                        pool.resource[resource_name] = resource

                self.logger.info("<compute_pool_manager> %d resources loaded for pool '%s'" % (resource_count, pool.name))

                self.compute_pool[pool_id] = pool

            self.logger.info("<compute_pool_manager> %d pool loaded in '%s'" % (pool_count, list_file))
            return True

    def savePoolList(self):
        with self.lock:
            # #remove invalid path
            pool_id_list = self.compute_pool.keys()
            name_list = os.listdir(self.pool_path)
            for path_name in name_list:
                pool_path = os.path.join(self.pool_path, path_name)
                if os.path.isdir(pool_path):
                    if path_name not in pool_id_list:
                        # #invalid uuid
                        self.logger.info("<compute_pool_manager> remove invalid pool path '%s'" % (pool_path))
                        shutil.rmtree(pool_path)

            parser = ConfigParser()
            data_count = len(self.compute_pool)
            parser.set("DEFAULT", "data_count", data_count)
            index = 0
            for data in self.compute_pool.values():
                parser.set("DEFAULT", "uuid_%d" % (index), data.uuid)
                index += 1

            list_file = os.path.join(self.pool_path, "compute_pool.info")
            with io.open(list_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<compute_pool_manager> %d pool saved into '%s'" % (data_count, list_file))
            return True

    def savePoolInfo(self, pool_id):
        with self.lock:

            if not self.compute_pool.has_key(pool_id):
                self.logger.error("<compute_pool_manager> save pool info fail, invalid pool id '%s'" % (pool_id))
                return False

            pool = self.compute_pool[pool_id]

            parser = ConfigParser()
            parser.set("DEFAULT", "name", pool.name)
            parser.set("DEFAULT", "uuid", pool.uuid)
            parser.set("DEFAULT", "status", pool.status)
            parser.set("DEFAULT", "network", pool.network)
            parser.set("DEFAULT", "network_type", pool.network_type)
            parser.set("DEFAULT", "disk_type", pool.disk_type)
            parser.set("DEFAULT", "disk_source", pool.disk_source)
            parser.set("DEFAULT", "high_available", pool.high_available)
            parser.set("DEFAULT", "auto_qos", pool.auto_qos)
            parser.set("DEFAULT", "thin_provisioning", pool.thin_provisioning)
            parser.set("DEFAULT", "backing_image", pool.backing_image)
            parser.set("DEFAULT", "path", pool.path)
            parser.set("DEFAULT", "crypt", pool.crypt)

            resource_count = len(pool.resource)
            parser.set("DEFAULT", "resource_count", resource_count)
            if 0 != resource_count:
                index = 0
                for resource_name in pool.resource.keys():
                    parser.set("DEFAULT", "resource_%d" % (index), resource_name)
                    index += 1

            path = os.path.join(self.pool_path, pool.uuid)
            if not os.path.exists(path):
                os.mkdir(path)

            info_file = os.path.join(path, "pool.info")

            with io.open(info_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<compute_pool_manager> pool '%s' saved into '%s'" % (pool.name, info_file))
            return True

    def savePoolResource(self, pool_id, resource_name):
        with self.lock:
            if not self.compute_pool.has_key(pool_id):
                self.logger.error("<compute_pool_manager> save pool resource fail, invalid pool id '%s'" % (
                        pool_id))
                return False
            pool = self.compute_pool[pool_id]
            if not pool.resource.has_key(resource_name):
                self.logger.error("<compute_pool_manager> save pool resource fail, invalid resource '%s'" % (
                        resource_name))
                return False

            resource = pool.resource[resource_name]
            parser = ConfigParser()
            parser.set("DEFAULT", "name", resource.name)
            parser.set("DEFAULT", "server", resource.server)
            parser.set("DEFAULT", "status", resource.status)

            host_count = len(resource.allocated)
            parser.set("DEFAULT", "host_count", host_count)
            if 0 != host_count:
                index = 0
                for host_id in resource.allocated:
                    parser.set("DEFAULT", "host_%d" % (index), host_id)
                    index += 1

            path = os.path.join(self.pool_path, pool_id)
            if not os.path.exists(path):
                os.mkdir(path)

            resource_file = os.path.join(path, "resource_%s.info" % (resource_name))

            with io.open(resource_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<compute_pool_manager> resource '%s' saved into '%s'" % (
                    resource_name, resource_file))
            return True

    def deleteResourceFile(self, pool_id, resource_name):
        with self.lock:
            path = os.path.join(self.pool_path, pool_id)
            file_name = os.path.join(path, "resource_%s.info" % (resource_name))
            if os.path.exists(file_name):
                os.remove(file_name)

    def deletePoolPath(self, pool_id):
        with self.lock:
            path = os.path.join(self.pool_path, pool_id)
            if os.path.exists(path):
                shutil.rmtree(path)

    def queryAllPool(self):
        with self.lock:
            return self.compute_pool.values()

    def createPool(self, config):
        with self.lock:
            for pool in self.compute_pool.values():
                if pool.name == config.name:
                    self.logger.error("<compute_pool_manager> create pool fail, pool '%s' already exists" % (config.name))
                    return False
            config.uuid = uuid.uuid4().hex
            config.status = ResourceStatusEnum.enable
            self.compute_pool[config.uuid] = config
            self.logger.info("<compute_pool_manager> create pool success, pool '%s'('%s')" % (config.name, config.uuid))
            self.savePoolList()
            self.savePoolInfo(config.uuid)
            return True

    def modifyPool(self, uuid, config):
        with self.lock:
            if not self.compute_pool.has_key(uuid):
                self.logger.error("<compute_pool_manager> modify pool fail, invalid pool id '%s'" %
                                  (uuid))
                return False

            for pool in self.compute_pool.values():
                if pool.uuid != uuid and pool.name == config.name:
                    self.logger.error("<compute_pool_manager> modify pool fail, duplicate pool name '%s'" %
                                      (config.name))
                    return False

            pool = self.compute_pool[uuid]

            pool.name = config.name
            pool.status = config.status
            pool.network = config.network
            pool.network_type = config.network_type
            pool.disk_type = config.disk_type
            pool.disk_source = config.disk_source
            pool.high_available = config.high_available
            pool.auto_qos = config.auto_qos
            pool.thin_provisioning = config.thin_provisioning
            pool.backing_image = config.backing_image
            pool.path = config.path
            pool.crypt = config.crypt

            self.logger.info("<compute_pool_manager> modify pool success, pool '%s'('%s')" % (pool.name, pool.uuid))

            self.savePoolInfo(uuid)
            return True

    def deletePool(self, uuid):
        with self.lock:
            if not self.compute_pool.has_key(uuid):
                self.logger.error("<compute_pool_manager> delete pool fail, invalid pool id '%s'" % (
                        uuid))
                return False
            pool = self.compute_pool[uuid]
            if not pool.isEmpty():
                self.logger.error("<compute_pool_manager> delete pool fail, pool '%s' not empty" % (
                        pool.name))
                return False
            self.logger.info("<compute_pool_manager> delete pool success, pool '%s'('%s')" % (
                pool.name, pool.uuid))
            del self.compute_pool[uuid]
            self.deletePoolPath(uuid)
            self.savePoolList()
            return True

    def containsPool(self, pool_id):
        with self.lock:
            return self.compute_pool.has_key(pool_id)

    def getPool(self, uuid):
        with self.lock:
            if not self.compute_pool.has_key(uuid):
                return None
            else:
                return self.compute_pool[uuid]

    def addResource(self, pool_id, resource_list):
        with self.lock:
            if not self.compute_pool.has_key(pool_id):
                self.logger.error("<compute_pool_manager> add resource fail, invalid pool id '%s'" % (
                                                                                          pool_id))
                return False
            pool = self.compute_pool[pool_id]
            count = 0
            for resource in resource_list:
                if not pool.resource.has_key(resource.name):
                    resource.status = ResourceStatusEnum.enable
                    pool.resource[resource.name] = resource
                    self.savePoolResource(pool_id, resource.name)
                    self.logger.info("<compute_pool_manager> add resource success, add resource '%s' to pool '%s'" % (
                                                                                                          resource.name, pool.name))
                    count += 1

            if 0 != count:
                self.savePoolInfo(pool_id)
            return True

    def removeResource(self, pool_id, name_list):
        with self.lock:
            if not self.compute_pool.has_key(pool_id):
                self.logger.error("<compute_pool_manager> remove resource fail, invalid pool id '%s'" % (
                        pool_id))
                return False
            pool = self.compute_pool[pool_id]
            count = 0
            for name in name_list:
                if pool.resource.has_key(name):
                    resource = pool.resource[name]
                    if 0 != len(resource.allocated):
                        self.logger.error("<compute_pool_manager> remove resource fail, resource '%s' not empty" % (
                            name))
                        continue
                    del pool.resource[name]
                    self.deleteResourceFile(pool_id, name)
                    self.logger.info("<compute_pool_manager> remove resource success, remove resource '%s' from pool '%s'" % (
                        name, pool.name))
                    count += 1

            if 0 != count:
                self.savePoolInfo(pool_id)
                return True
            else:
                return False

    def queryResource(self, pool_id):
        with self.lock:
            result = []
            if not self.compute_pool.has_key(pool_id):
                return result
            pool = self.compute_pool[pool_id]
            for resource in pool.resource.values():
                result.append(resource)
            return result

    def searchResource(self, name):
        """
        @return:contains, pool_id
        """
        with self.lock:
            for pool_id in self.compute_pool.keys():
                compute_pool = self.compute_pool[pool_id]
                if compute_pool.resource.has_key(name):
                    return True, pool_id
            else:
                return False, ""

    def containsResource(self, pool_id, name):
        with self.lock:
            if not self.compute_pool.has_key(pool_id):
                return False
            compute_pool = self.compute_pool[pool_id]
            return compute_pool.resource.has_key(name)

    def getResource(self, pool_id, name):
        with self.lock:
            if not self.compute_pool.has_key(pool_id):
                return None
            compute_pool = self.compute_pool[pool_id]
            if compute_pool.resource.has_key(name):
                return compute_pool.resource[name]
            else:
                return None

    def containNetwork(self, network):
        if len(strip(network)) != 0:
            with self.lock:
                for pool in self.compute_pool.values():
                    pool_network = pool.network
                    if len(strip(pool_network)) != 0 and pool_network == network:
                        return True

        return  False

#!/usr/bin/python
import logging
import threading
import uuid
import os
import os.path
import io
import shutil
from ConfigParser import *
from address_pool import *
from address_resource import *

class AddressManager(object):
    
    def __init__(self, resource_path, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.root_path = os.path.join(resource_path, "address")        
        if not os.path.exists(self.root_path):
            os.mkdir(self.root_path)
            
        ##key = uuid, value = AddressPool
        self.address_pool = {}
        ##lazy save
        self.modified = False
        self.lock = threading.RLock()
        
    def load(self):
        with self.lock:
            list_file = os.path.join(self.root_path, "pool_list.info")
            if not os.path.exists(list_file):
                ##create default pool
                default_config = AddressPool()
                default_config.name = "default"
                self.createPool(default_config)
                self.save()
                return True
            self.address_pool = {}
            parser = ConfigParser()
            parser.read(list_file)
            pool_count = parser.getint("DEFAULT", "data_count")
            pool_id_list = []
            for index in range(pool_count):
                pool_id_list.append(parser.get("DEFAULT", "uuid_%d"%(index)))

            for pool_id in pool_id_list:
                pool_path = os.path.join(self.root_path, pool_id)
                info_file = os.path.join(pool_path, "pool.info")
                if not os.path.exists(info_file):
                    continue
                parser.read(info_file)

                pool = AddressPool()
                pool.name = parser.get("DEFAULT", "name")        
                pool.uuid = parser.get("DEFAULT", "uuid")        
                pool.enable = parser.getboolean("DEFAULT", "enable")
                resource_count = parser.getint("DEFAULT", "resource_count")

                if 0 != resource_count:
                    resource_list = []
                    for index in range(resource_count):
                        resource_list.append(parser.get("DEFAULT", "resource_%d"%(index)))

                    for resource_name in resource_list:
                        resource_file = os.path.join(pool_path, "resource_%s.info"%(resource_name))
                        parser.read(resource_file)
                        
                        resource_ip = parser.get("DEFAULT", "ip")        
                        resource_count = parser.getint("DEFAULT", "count")
                        resource = AddressResource(resource_ip,
                                                   resource_count)
                        
                        resource.enable = parser.getboolean("DEFAULT", "enable")
                        
                        address_count = parser.getint("DEFAULT", "address_count")
                        if 0 != address_count:
                            for index in range(address_count):
                                int_address = parser.getint("DEFAULT", "address_%d"%(index))
                                resource.allocated.add(int_address)
                                
                        resource.setModified(False)                            
                        pool.resource[resource_name] = resource
                self.logger.info("<AddressPool>%d resources loaded for pool '%s'"%(
                    resource_count, pool.name))
                pool.setModified(False)
                self.address_pool[pool_id] = pool
                
            self.logger.info("<AddressPool>%d pool loaded in '%s'"%(
                    pool_count, list_file))
            return True           

    def save(self):
        self.syncPoolList()
        self.syncPoolInfo()
        self.syncResource()

    def syncPoolList(self):
        with self.lock:        
            ##remove invalid path
            pool_id_list = self.address_pool.keys()
            name_list = os.listdir(self.root_path)
            for path_name in name_list:
                pool_path = os.path.join(self.root_path, path_name)
                if os.path.isdir(pool_path):
                    if path_name not in pool_id_list:
                        ##invalid uuid
                        self.logger.info("<AddressPool>remove invalid pool path '%s'"%(
                            pool_path))
                        shutil.rmtree(pool_path)
                        
            if not self.modified:
                return
            parser = ConfigParser()
            data_count = len(self.address_pool)
            parser.set("DEFAULT", "data_count", data_count)        
            index = 0
            for data in self.address_pool.values():
                parser.set("DEFAULT", "uuid_%d"%(index), data.uuid)              
                index += 1                
            list_file = os.path.join(self.root_path, "pool_list.info")
            with io.open(list_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<AddressPool>%d pool saved into '%s'"%(
                    data_count, list_file))
            self.modified = False
            return True
    
    def syncPoolInfo(self):
        with self.lock:
            for pool in self.address_pool.values():
                if pool.isModified():
                    ##save                
                    parser = ConfigParser()
                    parser.set("DEFAULT", "name", pool.name)        
                    parser.set("DEFAULT", "uuid", pool.uuid)        
                    parser.set("DEFAULT", "enable", pool.enable)
                    resource_count = len(pool.resource)
                    parser.set("DEFAULT", "resource_count", resource_count)
                    if 0 != resource_count:
                        index = 0
                        for start_ip in pool.resource.keys():
                            parser.set("DEFAULT", "resource_%d"%(index), start_ip)
                            index += 1

                    pool_path = os.path.join(self.root_path, pool.uuid)
                    if not os.path.exists(pool_path):
                        os.mkdir(pool_path)
                        
                    info_file = os.path.join(pool_path, "pool.info")
                    
                    with io.open(info_file, "wb") as storage:
                        parser.write(storage)
                        self.logger.info("<AddressPool>pool '%s' saved into '%s'"%(
                            pool.name, info_file))
                    pool.setModified(False)
            return True
            
    def syncResource(self):
        with self.lock:
            for pool in self.address_pool.values():
                resource_list = pool.getAllResource()
                for resource in resource_list:
                    if resource.isModified():
                        parser = ConfigParser()
                        parser.set("DEFAULT", "ip", resource.ip)        
                        parser.set("DEFAULT", "count", resource.count)        
                        parser.set("DEFAULT", "enable", resource.enable)        
                        
                        address_count = resource.allocatedCount()
                        parser.set("DEFAULT", "address_count", address_count)
                        if 0 != address_count:
                            index = 0
                            for int_address in resource.getAllocated():
                                parser.set("DEFAULT", "address_%d"%(index), int_address)
                                index += 1
                        pool_path = os.path.join(self.root_path, pool.uuid)
                        
                        resource_file = os.path.join(pool_path, "resource_%s.info"%(resource.ip))
                        
                        with io.open(resource_file, "wb") as storage:
                            parser.write(storage)
                            self.logger.info("<AddressPool>resource '%s' saved into '%s'"%(
                                resource.ip, resource_file))
                        resource.setModified(False)

    def queryAllPool(self):
        with self.lock:
            return self.address_pool.values()

    def createPool(self, config):
        with self.lock:
            for pool in self.address_pool.values():
                if pool.name == config.name:
                    self.logger.error("<AddressPool>create pool fail, pool '%s' already exists"%(
                        config.name))
                    return False
            if 0 == len(config.uuid):
                config.uuid = uuid.uuid4().hex
            self.address_pool[config.uuid] = config
            self.logger.info("<AddressPool>create pool success, pool '%s'('%s')"%(
                config.name, config.uuid))
            if not self.modified:
                self.modified = True
            return True

    def deletePool(self, uuid):
        with self.lock:
            if not self.address_pool.has_key(uuid):
                self.logger.error("<AddressPool>delete pool fail, invalid id '%s'"%(
                        uuid))
                return False
            pool = self.address_pool[uuid]
            ##if empty
            if not pool.isEmpty():
                self.logger.error("<AddressPool>delete pool fail, pool '%s' not empty"%(
                        pool.name))
                return False
            self.logger.info("<AddressPool>delete pool success, pool '%s'('%s')"%(
                pool.name, pool.uuid))        
            del self.address_pool[uuid]        
            if not self.modified:
                self.modified = True
            return True
    
    def containsPool(self, uuid):
        with self.lock:
            return self.address_pool.has_key(uuid)

    def getPool(self, uuid):
        with self.lock:
            if self.address_pool.has_key(uuid):
                return self.address_pool[uuid]
            else:
                return None

    def queryResource(self, pool_id):
        with self.lock:
            if not self.address_pool.has_key(pool_id):
                return []
            pool = self.address_pool[pool_id]
            return pool.getAllResource()            

    def statisticStatus(self):
        """
        @return:[idle, allocated]
        """
        with self.lock:
            allocated = 0
            idle = 0
            total = 0
            for pool in self.address_pool.values():
                pool_available, pool_total = pool.statistic()
                idle += pool_available
                total += pool_total
            allocated = total - idle
            return [idle, allocated]
    
    
    def allocate(self, pool_id):
        with self.lock:
            # instance of AddressPool
            if not self.address_pool.has_key(pool_id):
                self.logger.error("<address_manager> cannot allocate ip, invalid address pool '%s'" % (pool_id))
                return None
            pool = self.address_pool[pool_id]
            return pool.allocate()
        
    
    def deallocate(self, pool_id, ip):
        with self.lock:
            
            if not bool(ip):
                self.logger.error("<address_manager> cannot deallocate ip '%s'" % (ip))
                return False
            
            # AddressPool
            if not self.address_pool.has_key(pool_id):
                self.logger.error("<address_manager> cannot deallocate ip, invalid address pool id '%s'" % pool_id)
                return False
            
            pool = self.address_pool[pool_id]
            
            b =  pool.deallocate(ip)
            return b
        

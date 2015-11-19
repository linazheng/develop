#!/usr/bin/python
import logging
import threading
import uuid
import os
import os.path
import io
import shutil
from ConfigParser import *
from port_pool import *
from port_resource import *

class PortManager(object):
    
    def __init__(self, resource_path, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.root_path = os.path.join(resource_path, "port")        
        if not os.path.exists(self.root_path):
            os.mkdir(self.root_path)
        ##key = uuid, value = Port Pool
        self.port_pool = {}
        ##lazy save
        self.modified = False
        self.lock = threading.RLock()

    def load(self):
        with self.lock:
            list_file = os.path.join(self.root_path, "pool_list.info")
            
            if not os.path.exists(list_file):
                # create default pool
                default_config = PortPool()
                default_config.name = "default"
                self.createPool(default_config)
                self.save()
                return True
            
            self.port_pool = {}
            parser = ConfigParser()
            
            # read 'pool_list.info'
            parser.read(list_file)
            pool_count = parser.getint("DEFAULT", "data_count")
            pool_id_list = []
            for index in range(pool_count):
                pool_id_list.append(parser.get("DEFAULT", "uuid_%d"%(index)))

            for pool_id in pool_id_list:
                pool_path = os.path.join(self.root_path, pool_id)
                # read '/resource/port/c8bce8010d934d60a03bedf8fa42e4e6/pool.info'
                info_file = os.path.join(pool_path, "pool.info")
                if not os.path.exists(info_file):
                    continue
                
                # read 'pool.info'
                parser.read(info_file)
                pool = PortPool()
                pool.name      = parser.get("DEFAULT",        "name")        
                pool.uuid      = parser.get("DEFAULT",        "uuid")        
                pool.enable    = parser.getboolean("DEFAULT", "enable")
                
                resource_count = parser.getint("DEFAULT",     "resource_count")
                if 0 != resource_count:
                    resource_list = []
                    for index in range(resource_count):
                        resource_list.append(parser.get("DEFAULT", "resource_%d"%(index)))

                    for resource_name in resource_list:
                        
                        resource_file = os.path.join(pool_path, "resource_%s.info"%(resource_name))
                        
                        # read 'resource_1.1.1.1.info'
                        parser.read(resource_file)

                        resource = PortResource()
                        resource.ip     = parser.get("DEFAULT",        "ip")                            
                        resource.enable = parser.getboolean("DEFAULT", "enable")
                        
                        port_count = parser.getint("DEFAULT", "port_count")
                        if 0 != port_count:
                            for index in range(port_count):
                                allocated_port = parser.get("DEFAULT", "port_%d"%(index))
                                resource.allocated.add(int(allocated_port))
                                
                        resource.setModified(False)                            
                        pool.resource[resource_name] = resource
                        
                self.logger.info("<PortPool>%d resources loaded for pool '%s'"%(resource_count, pool.name))
                pool.setModified(False)
                self.port_pool[pool_id] = pool
                
            self.logger.info("<PortPool>%d pool loaded in '%s'"%(pool_count, list_file))
            return True
            

    def save(self):
        self.syncPoolList()
        self.syncPoolInfo()
        self.syncResource()

    def syncPoolList(self):
        with self.lock:
            ##remove invalid path
            pool_id_list = self.port_pool.keys()
            name_list = os.listdir(self.root_path)
            for path_name in name_list:
                pool_path = os.path.join(self.root_path, path_name)
                if os.path.isdir(pool_path):
                    if path_name not in pool_id_list:
                        ##invalid uuid
                        self.logger.info("<PortPool>remove invalid pool path '%s'"%(pool_path))
                        shutil.rmtree(pool_path)
                        
            if not self.modified:
                return
            parser = ConfigParser()
            data_count = len(self.port_pool)
            parser.set("DEFAULT", "data_count", data_count)        
            index = 0
            for data in self.port_pool.values():
                parser.set("DEFAULT", "uuid_%d"%(index), data.uuid)              
                index += 1                
            list_file = os.path.join(self.root_path, "pool_list.info")
            with io.open(list_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<PortPool>%d pool saved into '%s'"%(data_count, list_file))
            self.modified = False
            return True
    
    def syncPoolInfo(self):
        with self.lock:
            for pool in self.port_pool.values():
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
                        for ip in pool.resource.keys():
                            parser.set("DEFAULT", "resource_%d"%(index), ip)
                            index += 1

                    pool_path = os.path.join(self.root_path, pool.uuid)
                    if not os.path.exists(pool_path):
                        os.mkdir(pool_path)
                        
                    info_file = os.path.join(pool_path, "pool.info")
                    
                    with io.open(info_file, "wb") as storage:
                        parser.write(storage)
                        self.logger.info("<PortPool>pool '%s' saved into '%s'"%(pool.name, info_file))
                    pool.setModified(False)
            return True
            
    def syncResource(self):
        with self.lock:
            for pool in self.port_pool.values():
                resource_list = pool.getAllResource()
                
                for resource in resource_list:
                    if resource.isModified():
                        parser = ConfigParser()
                        parser.set("DEFAULT", "ip",         resource.ip)              
                        parser.set("DEFAULT", "enable",     resource.enable)        
                        
                        port_count = resource.allocatedCount()
                        parser.set("DEFAULT", "port_count", port_count)
                        if 0 != port_count:
                            index = 0
                            for allocated_port in resource.getAllocated():
                                parser.set("DEFAULT", "port_%d"%(index), allocated_port)
                                index += 1
                                
                        pool_path = os.path.join(self.root_path, pool.uuid)
                        
                        resource_file = os.path.join(pool_path, "resource_%s.info"%(resource.ip))
                        
                        with io.open(resource_file, "wb") as storage:
                            parser.write(storage)
                            self.logger.info("<PortPool>resource '%s' saved into '%s'"%(resource.ip, resource_file))
                            
                        resource.setModified(False)

    def queryAllPool(self):
        with self.lock:
            return self.port_pool.values()

    def createPool(self, config):
        with self.lock:
            for pool in self.port_pool.values():
                if pool.name == config.name:
                    self.logger.error("<PortPool>create pool fail, pool '%s' already exists"%(
                        config.name))
                    return False
            if 0 == len(config.uuid):
                config.uuid = uuid.uuid4().hex
            self.port_pool[config.uuid] = config
            self.logger.info("<PortPool>create pool success, pool '%s'('%s')"%(
                config.name, config.uuid))
            if not self.modified:
                self.modified = True
            return True

    def deletePool(self, uuid):
        with self.lock:
            if not self.port_pool.has_key(uuid):
                self.logger.error("<PortPool>delete pool fail, invalid id '%s'"%(
                                                                                 uuid))
                return False
            
            pool = self.port_pool[uuid]
            
            ##if empty
            if not pool.isEmpty():
                self.logger.error("<PortPool>delete pool fail, pool '%s' not empty"%(
                                                                                     pool.name))
                return False
            self.logger.info("<PortPool>delete pool success, pool '%s'('%s')"%(
                                                                               pool.name, pool.uuid))        
            del self.port_pool[uuid]        
            if not self.modified:
                self.modified = True
            return True
    
    def containsPool(self, uuid):
        with self.lock:
            return self.port_pool.has_key(uuid)

    def getPool(self, uuid):
        with self.lock:
            if self.port_pool.has_key(uuid):
                return self.port_pool[uuid]
            else:
                return None
            
    def queryResource(self, pool_id):
        with self.lock:
            if not self.port_pool.has_key(pool_id):
                return []
            pool = self.port_pool[pool_id]
            return pool.getAllResource()            

    def statisticStatus(self):
        """
        @return:[idle, allocated]
        """
        with self.lock:
            allocated = 0
            idle = 0
            total = 0
            for pool in self.port_pool.values():
                pool_available, pool_total = pool.statistic()
                idle += pool_available
                total += pool_total
            allocated = total - idle
            return [idle, allocated]    
    
    def allocate(self, pool_id, count):
        """
        @return: ip, port_list
        """
        count = int(count)
        with self.lock:
            if not self.port_pool.has_key(pool_id):
                return None, None
            pool = self.port_pool[pool_id]
            rt_ip, rt_port_list = pool.allocate(count)
            return rt_ip, rt_port_list

    def allocatePort(self, pool_id, ip, count):
        """
        @return:ip, port_list
        """
        with self.lock:
            if not self.port_pool.has_key(pool_id):
                return None
            pool = self.port_pool[pool_id]
            return pool.allocatePort(ip, count)
    
    def deallocate(self, pool_id, ip, port_lost):
        with self.lock:
            if not self.port_pool.has_key(pool_id):
                return False
            pool = self.port_pool[pool_id]
            return pool.deallocate(ip, port_lost)
    

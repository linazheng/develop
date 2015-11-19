#!/usr/bin/python

from port_resource import PortResource
import logging

class PortPool(object):
    
    def __init__(self):
        self.logger = logging.getLogger("PortPool")
        self.name = ""
        self.uuid = ""
        self.enable = True
        ##key = ip, value = PorlResource
        self.resource = {}
        self.modified = True
        
    def setModified(self, modified):
        self.modified = modified
    
    def isModified(self):
        return self.modified
    
    def statistic(self):
        """
        @return:available, total
        """
        available = 0
        total = 0
        for resource in self.resource.values():
            resource_available, resource_total = resource.statistic()
            available += resource_available
            total += resource_total
        return available, total

    def isEmpty(self):
        available, total = self.statistic()
        return available == total    

    def addResource(self, ip_list):
        for ip in ip_list:
            if self.resource.has_key(ip):
                return False
        for ip in ip_list:
            resource = PortResource()
            resource.ip = ip
            self.resource[ip] = resource
        self.modified = True
        return True

    def removeResource(self, ip_list):
        for ip in ip_list:
            if not self.resource.has_key(ip):
                ##invalid ip
                return False
            resource = self.resource[ip]
            if not resource.isEmpty():
                return False
        for ip in ip_list:
            del self.resource[ip]
            
        self.modified = True
        return True

    def getAllResource(self):
        return self.resource.values()

    def allocate(self, count):
        """
        @return:ip, port_list
        """
        count = int(count)
        for ip in self.resource.keys():
            resource = self.resource[ip]            
            if resource.isAvailable(count):
                port_list = resource.allocate(count)
                if port_list is not None:
                    ##success
                    return ip, port_list
        else:
            return None, None
        
    def allocatePort(self, ip, count):
        """
        @return:port_list
        """
        if not self.resource.has_key(ip):
            return None
        resource = self.resource[ip]            
        if resource.isAvailable(count):
            port_list = resource.allocate(count)
            if port_list is not None:
                ##success
                return port_list
        return None

    def deallocate(self, ip, port_list):
        if not self.resource.has_key(ip):
            return False
        resource = self.resource[ip]
        return resource.deallocate(port_list)

    def setAllocated(self, ip, port_list):
        if not self.resource.has_key(ip):
            return False
        resource = self.resource[ip]
        return resource.setAllocated(port_list)
    
    def isAllAllocated(self, ip, port_list):
        if not self.resource.has_key(ip):
            return False
        resource = self.resource[ip]
        return resource.isAllAllocated(port_list)
    
    def setUnallocated(self, ip, port_list):
        if not self.resource.has_key(ip):
            return False
        resource = self.resource[ip]
        return resource.setUnallocated(port_list)        

#!/usr/bin/python
import logging

class AddressPool(object):
    
    def __init__(self):
        self.logger = logging.getLogger("address_pool")
        self.name = ""
        self.uuid = ""
        self.enable = True
        ##key = start ip, value = AddressResource
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

    def addResource(self, resource_list):
        for new_resource in resource_list:
            ##check isCollide
            for exists_resource in self.resource.values():
                if exists_resource.ip == new_resource.ip:
                    return False
                if exists_resource.isCollide(new_resource.ip,
                                             new_resource.count):
                    return False
        for new_resource in resource_list:
            self.resource[new_resource.ip] = new_resource
        self.modified = True
        return True


    def removeResource(self, ip_list):
        
        for start_ip in ip_list:
            
            if not self.resource.has_key(start_ip):
                self.logger.error("<address_pool> remove resource fial, ip '%s' not in address pool '%s'" % (start_ip, self.uuid))
                ##invalid ip
                return False
            
            resource = self.resource[start_ip]
            if not resource.isEmpty():
                self.logger.error("<address_pool> remove resource fial, resource is not empty, ip '%s', address pool '%s'" % (start_ip, self.uuid))
                return False
            
        for start_ip in ip_list:
            del self.resource[start_ip]
            
        self.modified = True
        return True
    

    def getAllResource(self):
        return self.resource.values()

    def allocate(self):
        # AddressResource
        for resource in self.resource.values():
            if resource.isAvailable():
                return resource.allocate()
        else:
            return None

    def deallocate(self, ip):
        # AddressResource
        for resource in self.resource.values():
            if resource.inRange(ip):
                return resource.deallocate(ip)
        return False

    def setAllocated(self, ip):
        for resource in self.resource.values():
            if resource.inRange(ip):
                return resource.setAllocated(ip)
        return False

    def setUnallocated(self, ip):
        for resource in self.resource.values():
            if resource.inRange(ip):
                return resource.setUnallocated(ip)
        return False
    
    def isAvailableIp(self, ip):
        for resource in self.resource.values():
            if resource.inRange(ip):
                return resource.isAvailableIp(ip)
            
        return False
                
        

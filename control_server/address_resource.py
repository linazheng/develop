#!/usr/bin/python
from service.socket_util import *
import logging

class AddressResource(object):
    
    def __init__(self, start_ip, count):
        self.logger = logging.getLogger("address_resource")
        self.ip = start_ip
        self.count = count
        self.enable = True
        ##ip in int form
        self.allocated = set()
        self.begin_int = convertAddressToInt(start_ip)
        self.end_int = self.begin_int + count
        self.last_offset = 0
        self.modified = True
        
    def setModified(self, modified):
        self.modified = modified
        
    def isModified(self):
        return self.modified

    def allocatedCount(self):
        return len(self.allocated)

    def getAllocated(self):
        return self.allocated
    
    def statistic(self):
        """
        @return:available, total
        """
        allocated = len(self.allocated)
        return (self.count - allocated), self.count

    def isAvailable(self):
        if not self.enable:
            return False
        allocated = len(self.allocated)
        if allocated >= self.count:
            return False
        else:
            return True

    def isEmpty(self):
        return 0 == len(self.allocated)

    def isCollide(self, start_ip, count):
        begin_int = convertAddressToInt(start_ip)
        end_int = begin_int + count - 1
        target_begin = self.begin_int
        target_end = self.end_int - 1
        if (begin_int <= target_end) and (end_int >= target_begin):
            return True
        else:
            return False

    def inRange(self, ip):
        ip_int = convertAddressToInt(ip)
        if (ip_int >= self.begin_int) and (ip_int < self.end_int):
            return True
        else:
            return False

    def allocate(self):
        if not self.isAvailable():
            return None
        # begin = (self.last_offset + 1)% self.count
        begin = self.last_offset % self.count
        for offset in range(self.count):
            int_value = self.begin_int + (begin + offset)%self.count
            if int_value not in self.allocated:
                ##allocate
                self.allocated.add(int_value)
                if not self.modified:
                    self.modified = True
                self.last_offset = (begin + offset + 1)%self.count
                ip = convertIntToAddress(int_value)
                return ip
        else:
            return None

    def deallocate(self, ip):
        if self.isEmpty():
            return False
        ip_int = convertAddressToInt(ip)
        if ip_int in self.allocated:
            self.allocated.remove(ip_int)
            if not self.modified:
                self.modified = True
            return True
        else:
            return False
        
    def setAllocated(self, ip):
        int_value = convertAddressToInt(ip)
        if (int_value >= self.begin_int) and (int_value < self.end_int):
            if int_value not in self.allocated:
                ##allocate
                self.allocated.add(int_value)
                if not self.modified:
                    self.modified = True
                return True
        return False

    def setUnallocated(self, ip):
        int_value = convertAddressToInt(ip)
        if (int_value >= self.begin_int) and (int_value < self.end_int):
            if int_value in self.allocated:
                ##allocate
                self.allocated.remove(int_value)
                if not self.modified:
                    self.modified = True
                return True
        return False
    
    def isAvailableIp(self, ip):
        ip_int = convertAddressToInt(ip)
        if (ip_int >= self.begin_int) and (ip_int < self.end_int):
            if ip_int not in self.allocated:
                return True
        
        return False
            

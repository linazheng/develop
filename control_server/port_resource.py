#!/usr/bin/python
import logging

class PortResource(object):
    
    default_begin_port = 1024
    default_end_port = 65535
    
    def __init__(self):
        self.logger = logging.getLogger("PortResource")
        self.ip = ""
        self.enable = True        
        self.begin_port = PortResource.default_begin_port
        self.end_port   = PortResource.default_end_port
        self.count = self.end_port - self.begin_port
        self.last_offset = 0
        ##allocated port
        self.allocated = set()
        self.modified = True
        
    def setModified(self, modified):
        self.modified = modified
        
    def isModified(self):
        return self.modified

    def allocatedCount(self):
        return len(self.allocated)

    def getIP(self):
        return self.ip
    
    def getAllocated(self):
        return self.allocated
    
    def statistic(self):
        """
        @return:available, total
        """
        allocated = len(self.allocated)
        return (self.count - allocated), self.count

    def isAvailable(self, count):
        if not self.enable:
            return False
        allocated = len(self.allocated)
        if (allocated + count) >= self.count:
            return False
        else:
            return True

    def isEmpty(self):
        return 0 == len(self.allocated)

    def allocate(self, count):
        count = int(count)
        
        if not self.isAvailable(count):
            return None
        
        available = []
        begin = (self.last_offset) % self.count
        
        for port_offset in xrange(self.count):
            port = self.begin_port + (begin + port_offset) % self.count
            if port not in self.allocated:
                available = [port]
                for offset in xrange(1, count):
                    if (port + offset) in self.allocated:
                        break
                    available.append(port + offset)
                if len(available)!=count:
                    continue;
                
                ##all available
                for allocated_port in available:
                    self.allocated.add(allocated_port)
                    
                if not self.modified:
                    self.modified = True
                    
                self.last_offset = (begin + port_offset + len(available))%self.count
                return available
            
        return None

    def deallocate(self, port_list):
        if self.isEmpty():
            return False
        for port in port_list:
            if port in self.allocated:
                self.allocated.remove(port)
                self.modified = True
        return True

    def setAllocated(self, port_list):
        for port in port_list:
            if ( port >= self.begin_port) and (port < self.end_port):
                if port not in self.allocated:
                    self.allocated.add(port)
                    if not self.modified:
                        self.modified = True
        return True
    
    def isAllAllocated(self, port_list):
        for port in port_list:
            if ( port >= self.begin_port) and (port < self.end_port):
                if port not in self.allocated:
                    return False;
        return True;
    
    def setUnallocated(self, port_list):
        for port in port_list:
            if ( port >= self.begin_port) and (port < self.end_port):
                if port in self.allocated:
                    self.allocated.remove(port)
                    if not self.modified:
                        self.modified = True
        return True

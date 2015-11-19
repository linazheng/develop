#!/usr/bin/python
import sys
from service.daemon import * 
from service.service_proxy import *
from service.message_define import *
from control_service import *

class Proxy(ServiceProxy):
    
    def __init__(self):
        ServiceProxy.__init__(self, NodeTypeDefine.control_server)
        
    def createService(self):
        """
        create service instance, must override
        """
        if 0 == len(self.node):
            print "must specify node name for control server"
            return None
        
        service = ControlService(
            self.node, self.domain, self.ip,
            self.group_ip, self.group_port,
            self.server, self.rack, self.server_name, self)
        
        return service

if __name__ == "__main__":
    proxy = Proxy()
    daemon = Daemon(proxy)
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            daemon.start()
            sys.exit(0)
        elif 'stop' == sys.argv[1]:
            daemon.stop()
            sys.exit(0)
        elif 'restart' == sys.argv[1]:
            daemon.stop()
            daemon.start()
            sys.exit(0)
            
    print "control server version:%s"%(proxy.version)
    print "usage: ./main.py start|stop|restart\n"

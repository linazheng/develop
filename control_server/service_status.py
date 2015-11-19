#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum

class ServiceStatus(object):
    status_running = 0
    status_warning = 1
    status_error = 2
    status_stop = 3
    
    def __init__(self):
        self.name = ""
        self.type = 0
        self.group = ""
        self.ip = ""
        self.port = 0
        self.status = ServiceStatus.status_stop
        self.version = ""
        self.server = ""
        self.disk_type = ComputeStorageTypeEnum.local

    def isRunning(self):
        return (self.status == ServiceStatus.status_running)

    def isStopped(self):
        return (self.status == ServiceStatus.status_stop)

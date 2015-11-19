#!/usr/bin/python
from pool_status_enum import *

class ComputePoolStatus(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        ##[stop, warning, error, running]
        self.node = [0, 0, 0, 0]
        ##[stop, warning, error, running]
        self.host = [0, 0, 0, 0]
        self.cpu_count = 0
        self.cpu_usage = 0.0
        ##[available, total]
        self.memory = [0, 0]
        self.memory_usage = 0.0
        ##[available, total]
        self.disk_volume = [0,0]
        self.disk_usage = 0.0
        self.status = PoolStatusEnum.stop
        ##format "YYYY-MM-DD HH:MI:SS"
        self.timestamp = ""
        
    

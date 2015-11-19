#!/usr/bin/python
from status_enum import *

class SystemStatus(object):
    def __init__(self):
        ##[stop, warning, error, running]
        self.server = [0, 0, 0, 0]
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
        ##read_count, read_bytes, write_count, write_bytes, io_error
        self.disk_io = [0, 0, 0, 0, 0]
        ##receive_bytes, receive_packets, receive_error, receive_drop,
        ##send_bytes, send_packets, send_error, send_drop
        self.network_io = [0, 0, 0, 0, 0, 0, 0, 0]
        ##read, write, receive, send
        self.speed = [0, 0, 0, 0]
        self.status = StatusEnum.running
        ##format "YYYY-MM-DD HH:MI:SS"
        self.timestamp = ""
        
    

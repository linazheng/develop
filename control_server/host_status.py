#!/usr/bin/python

class HostStatusEnum(object):
    status_running = 0
    status_warning = 1
    status_error = 2
    status_stop = 3

class HostStatus(object):
    def __init__(self):
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
        self.status = HostStatusEnum.status_stop
        ##format "YYYY-MM-DD HH:MI:SS"
        self.timestamp = ""
        ##server uuid
        self.server = ""
        self.uuid = ""
        ##[target_ip, public_ip]
        self.ip = ["",""]
        
    

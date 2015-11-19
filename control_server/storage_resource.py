#!/usr/bin/python

class StorageResource(object):
    
    def __init__(self):
        self.storage_pool = ""
        self.name         = ""
        self.status       = 0
        self.cpu_count    = 0
        self.cpu_usage    = 0.0
        self.memory       = []
        self.memory_usage = 0.0
        self.disk_volume  = []
        self.disk_usage   = 0.0
        self.ip           = ""

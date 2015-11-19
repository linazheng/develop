#!/usr/bin/python

# class StorageTypeEnum(object):
#     normal = 0
#     fast = 1

class StoragePool(object):
    
    def __init__(self):
        self.data_index   = ""
        self.uuid         = ""
        self.name         = ""
        self.node         = []
        self.disk         = []
        self.cpu_count    = 0
        self.cpu_usage    = 0.0
        self.memory       = []
        self.memory_usage = 0.0
        self.disk_volume  = []
        self.disk_usage   = 0.0
        self.status       = 0
    
#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum

class ISOImage(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.enabled = True
        self.size = 0
        self.description = ""
        self.ip = ""
        self.port = 0
        self.group = ""
        self.user = ""
        self.path = ""  # nas path
        self.disk_type = ComputeStorageTypeEnum.local
        # #storage service name
        self.container = ""

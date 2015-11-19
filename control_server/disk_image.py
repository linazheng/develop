#!/usr/bin/python
from compute_pool import ComputeStorageTypeEnum

class DiskImageFileTypeEnum(object):
    raw = 0
    qcow2 = 1

class DiskImage(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.enabled = True
        self.size = 0
        self.tags = []
        self.description = ""
        self.group = ""
        self.user = ""
        self.path = ""  # nas path
        self.disk_type = ComputeStorageTypeEnum.local
        self.file_type = DiskImageFileTypeEnum.raw
        # #storage service
        self.container = ""

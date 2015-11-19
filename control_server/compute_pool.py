#!/usr/bin/python

class ComputeStorageTypeEnum(object):
    local = 0
    cloud = 1
    nas = 2
    ip_san = 3

class ComputeNetworkTypeEnum(object):
    private = 0
    monopoly = 1
    share = 2
    bridge = 3
    
class HighAvaliableModeEnum(object):
    disabled = 0
    enabled = 1
    
class AutoQOSModeEnum(object):
    disabled = 0
    enabled = 1
    

class ThinProvisioningModeEnum(object):
    disabled = 0
    enabled = 1
    

class BackingImageModeEnum(object):
    disabled = 0
    enabled = 1

class ComputePool(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.status = 0
        ##network pool uuid
        self.network = ""
        self.network_type = ComputeNetworkTypeEnum.private
        self.disk_type = ComputeStorageTypeEnum.local
        ##uuid for storage pool, when using cloud storage
        self.disk_source = ""
        self.high_available = HighAvaliableModeEnum.disabled
        self.auto_qos = AutoQOSModeEnum.disabled
        self.path = ""
        self.crypt = ""
        ##key = name, value = compute resource
        self.resource = {}
        self.thin_provisioning = ThinProvisioningModeEnum.disabled
        self.backing_image     = BackingImageModeEnum.disabled

    def isEmpty(self):
        if 0 == len(self.resource):
            return True
        else:
            return False
        
        

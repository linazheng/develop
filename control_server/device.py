#!/usr/bin/python


# cloud disk
class Device(object):
    
    def __init__(self):
        self.storage_pool = ""
        self.uuid         = ""
        self.name         = ""
        self.status       = 0
        self.disk_volume  = []
        self.level        = 0
        self.identity     = ""
        self.security     = 0
        self.crypt        = 0
        self.page         = 0
        
    
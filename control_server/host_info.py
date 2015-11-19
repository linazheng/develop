#!/usr/bin/python
from compute_pool import ThinProvisioningModeEnum, BackingImageModeEnum


class PortProtocolEnum(object):
    all_protocol = 0
    tcp_protocol = 1
    udp_protocol = 2


class NetworkTypeEnum(object):
    private = 0
    mono = 1
    share = 2


class DiskTypeEnum(object):
    local = 0
    cloud = 1


class EnableLocalBackupEnum(object):
    disabled = 0
    enabled = 1


class EnableUsbExtEnum(object):
    disabled = 0
    enabled = 1

class BackupHostModeEnum(object):
    fully = 0
    partial = 1
    
class VideoTypeEnum(object):
    mjpeg = 0
    h264 = 1

class HostPort(object):
    def __init__(self):
        self.server_port = 0
        self.host_port = 0
        self.public_ip = ""
        self.public_port = 0
        self.protocol = PortProtocolEnum.all_protocol


class HostInfo(object):
    def __init__(self):
        self.container = ""
        self.uuid = ""
        self.name = ""
        self.cpu_count = 0
        self.memory = 0
        self.auto_start = False
        self.data_disk_count = 0
        self.disk_volume = [0, 0]
        ##list of HostPort
        self.port = []
        self.user = ""
        self.group = ""
        self.display = ""
        self.authentication = ""
        self.network = ""
        self.inbound_bandwidth = 0
        self.outbound_bandwidth = 0
        self.max_iops = 0
        self.cpu_priority = 0
        self.server_ip = ""
        self.public_ip = ""
        ##display port in server
        self.server_port = 0
        ##display port in public
        self.public_port = 0
        ## output port range, content type of int
        self.output_port_range = []
        ##compute pool id
        self.pool = ""
        
        ##forwarder uuid
        self.forwarder = ""
        self.network_type = NetworkTypeEnum.private
        ##address pool id
        self.network_source = ""
        self.disk_type = DiskTypeEnum.local
        ##storage pool id
        self.disk_source = ""
        
#         self.vpc_network = ""
        self.vpc_ip = ""
        
        self.enable_local_backup = EnableLocalBackupEnum.disabled
        self.enable_usb_ext      = EnableUsbExtEnum.disabled
        self.thin_provisioning   = ThinProvisioningModeEnum.disabled
        self.backing_image       = BackingImageModeEnum.disabled
        self.video_type          = VideoTypeEnum.mjpeg
        
        
        
        
        
        
        
        
        
        
        
        
        

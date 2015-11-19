#!/usr/bin/python
import zlib
import logging
from common import json_util



class ForwarderTypeEnum(object):
    mono = 0
    share = 1
    domain = 2
    vpc = 3





class ForwarderPort(object):
    
    def __init__(self):
        self.protocol = 0
        self.server_port = 0
        self.host_port = 0
        self.public_ip = ""
        self.public_port = 0
        
    def toJSONString(self):
        _dict = {}
        _dict["protocol"]    = self.protocol
        _dict["server_port"] = self.server_port
        _dict["host_port"]   = self.host_port
        _dict["public_ip"]   = self.public_ip
        _dict["public_port"] = self.public_port
        return json_util.toJSONString(_dict)

    def computeSignature(self):
        data = "%s%s%s%s%s"%(
                self.protocol,
                self.server_port,
                self.host_port,
                self.public_ip,
                self.public_port)
        return zlib.crc32(data) & 0xffffffff





class HostForwarder(object):
    
    def __init__(self):
        self.logger = logging.getLogger("host_forwarder")
        self.uuid = ""
        self.type = ForwarderTypeEnum.mono
        
        self.host_id = ""
        self.host_name = ""
        
        self.public_ip = []
        self.public_monitor = 0
        
        self.server_ip = ""
        self.server_monitor = 0
        
        self.vpc_ip = ""
        self.vpc_range = ""
        
        self.output_port_range = []         # [min_port, max_port]
        
        ##list of ForwarderPort
        self.port = []
        self.enable = True
        self.crc = 0
        
    def copy(self):
        new_forwarder = HostForwarder()
        new_forwarder.uuid              = self.uuid             
        new_forwarder.type              = self.type                 
        new_forwarder.host_id           = self.host_id          
        new_forwarder.host_name         = self.host_name  
        new_forwarder.public_ip         = self.public_ip[:]  
        new_forwarder.public_monitor    = self.public_monitor    
        new_forwarder.server_ip         = self.server_ip        
        new_forwarder.server_monitor    = self.server_monitor          
        new_forwarder.vpc_ip            = self.vpc_ip          
        new_forwarder.vpc_range         = self.vpc_range       
        new_forwarder.output_port_range = self.output_port_range[:]
        new_forwarder.port              = self.port[:]             
        new_forwarder.enable            = self.enable           
        new_forwarder.crc               = self.crc     
        return new_forwarder   

    def computeSignature(self):
        data = "%s%s%s%s%s%s%s%s%s%s%s%s"%(
                self.uuid,
                self.type,
                self.public_ip,
                self.host_id,
                self.host_name,
                self.vpc_ip,
                self.vpc_range,
                self.server_ip,
                self.server_monitor,
                self.public_monitor,
                [int(x) for x in (self.output_port_range if bool(self.output_port_range) else [])],
                self.computePortSignature()
                )
        self.crc = zlib.crc32(data) & 0xffffffff
        return self.crc
        
    def computePortSignature(self):
        _len = len(self.port)
        _ports_crc = []
        for _port in self.port:
            _ports_crc.append(_port.computeSignature())
        data = ("%s"*_len) % tuple(_ports_crc)
        return zlib.crc32(data)&0xffffffff
        

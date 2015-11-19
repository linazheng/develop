#!/usr/bin/python


from service import socket_util
import threading
import logging


class NetworkStatus(object):
    disabled = 0
    enabled = 1


class NetworkInfo(object):
    
    
    def __init__(self):
        self.logger = logging.getLogger("network_info")
        self._lock = threading.RLock()
        self.uuid = ""
        self.name = ""
        self.size = 0
        self.description = ""
        self.pool = ""
        self.network_address = ""
        self.netmask = 0
        self.broadcast_address = ""
        self.status = NetworkStatus.disabled
        
        # containing host UUIDs
        self.hosts = set()
        
        # containing public ips
        self.public_ips = set()
        
        # containing allocated (inner vpc)ips
        self.allocated_ips = set()
        
        # key: "protocol:public_ip:public_port", value: "host_uuid:host_port"
        self.bound_ports = {}
        
    
    def copy(self):
        _newNetworkInfo = NetworkInfo()
        _newNetworkInfo.uuid              = self.uuid                      
        _newNetworkInfo.name              = self.name                      
        _newNetworkInfo.size              = self.size                      
        _newNetworkInfo.description       = self.description               
        _newNetworkInfo.pool              = self.pool                      
        _newNetworkInfo.network_address   = self.network_address           
        _newNetworkInfo.netmask           = self.netmask            
        _newNetworkInfo.broadcast_address = self.broadcast_address
        _newNetworkInfo.status            = self.status       
        _newNetworkInfo.hosts             = self.hosts.copy()                       
        _newNetworkInfo.public_ips        = self.public_ips.copy()               
        _newNetworkInfo.allocated_ips     = self.allocated_ips.copy()       
        _newNetworkInfo.bound_ports       = self.bound_ports.copy()
        return _newNetworkInfo
        
    
    def allocateIp(self, count):
        with self._lock:
            _result = []
            
            _intNetworkAddress   = socket_util.convertAddressToInt(self.network_address);
            _intBroadcastAddress = socket_util.convertAddressToInt(self.broadcast_address);
            
            _n = 0;
            for _ip in xrange(_intNetworkAddress+1, _intBroadcastAddress):
                _str_ip = socket_util.convertIntToAddress(_ip)
                if _str_ip not in self.allocated_ips:
                    _result.append(_str_ip)
                    _n += 1
                    if _n==count:
                        break;
                        
            if len(_result)<count:
                return None;
            
            for _ip in _result:
                self.allocated_ips.add(_ip)
                
            return _result
            
        
    def deallocateIp(self, ip):
        with self._lock:
            try:
                self.allocated_ips.remove(ip)
                return True
            except:
                return False
            
    
    def containsPublicIp(self, ip):
        return (ip in self.public_ips)
            
    
#     def isBoundPortExists(self, protocol, public_ip, public_port):
#         with self._lock:
#             _key = "%s:%s:%s" % (protocol, public_ip, public_port)
#             return self.bound_ports.has_key(_key)
    
    
    
        
        
        
        
        
        
        
        

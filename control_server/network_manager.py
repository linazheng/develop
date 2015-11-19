# encoding: utf8
import logging
import os
import uuid
import io
import threading
from ConfigParser import ConfigParser
from network_info import NetworkInfo
from service import socket_util
from collections import OrderedDict
from common import config_parser_util, dict_util
from string import strip


class NetworkManager(object):
    
    
    def __init__(self, resource_path, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.pool_path = os.path.join(resource_path, "network")
        
        if not os.path.exists(self.pool_path):
            os.mkdir(self.pool_path)
        
        # key = uuid, value = NetworkInfo
        self.network_info = {}
        
        self._min_ip = socket_util.convertAddressToInt("10.0.0.0");
        self._max_ip = socket_util.convertAddressToInt("10.255.255.255");
        
        # key = int_begin_ip, value = (int_begin_ip, int_end_ip, netmask, str_begin_ip, str_end_ip)
        self.network_resource = OrderedDict()
        self.is_sorted = True
        
        self._lock = threading.RLock()
    
    
    def load(self):
        with self._lock:
            self.loadAllNetwork()
    
    
    def loadAllNetwork(self):
        with self._lock:
            
            list_file = os.path.join(self.pool_path, "network_list.info")
            if not os.path.exists(list_file):
                return False
            
            self.network_info = {}
            parser = ConfigParser()
            
            # read 'network_list.info'
            parser.read(list_file)
            network_count = parser.getint("DEFAULT", "data_count")
            
            network_id_list = []
            for index in range(network_count):
                network_id_list.append(parser.get("DEFAULT", "uuid_%d"%(index)))
                
            for network_id in network_id_list:
                path              = os.path.join(self.pool_path, network_id)
                network_info_file = os.path.join(path, "network_info.info")
                if not os.path.exists(network_info_file):
                    continue
                
                # read '/var/zhicloud/config/control_server/resource/network/{network_uuid}/network_info.info'
                parser.read(network_info_file)

                _networkInfo = NetworkInfo()    
                _networkInfo.uuid              = config_parser_util.get(parser,       "DEFAULT",    "uuid")   
                _networkInfo.name              = config_parser_util.get(parser,       "DEFAULT",    "name")   
                _networkInfo.network_address   = config_parser_util.get(parser,       "DEFAULT",    "network_address")  
                _networkInfo.netmask           = config_parser_util.getint(parser,    "DEFAULT",    "netmask")      
                _networkInfo.broadcast_address = config_parser_util.get(parser,       "DEFAULT",    "broadcast_address")   
                _networkInfo.size              = config_parser_util.getint(parser,    "DEFAULT",    "size")          
                _networkInfo.description       = config_parser_util.get(parser,       "DEFAULT",    "description")   
                _networkInfo.pool              = config_parser_util.get(parser,       "DEFAULT",    "pool")     
                _networkInfo.status            = config_parser_util.getint(parser,    "DEFAULT",    "status")        
                
                # restore network resource
                _networkResourceItem = (socket_util.convertAddressToInt(_networkInfo.network_address),
                                        socket_util.convertAddressToInt(_networkInfo.broadcast_address),
                                        _networkInfo.netmask,
                                        _networkInfo.network_address,
                                        _networkInfo.broadcast_address)
                self.network_resource[_networkResourceItem[0]] = _networkResourceItem
                        
                # read [hosts] section
                _host_count = config_parser_util.getint(parser, "DEFAULT", "host_count", 0)
                if _host_count>0:
                    for i in xrange(_host_count):
                        _networkInfo.hosts.add( parser.get("hosts", ("host_%s" % i)) )
                        
                # read [public_ips] section
                _public_ip_count = config_parser_util.getint(parser, "DEFAULT", "public_ip_count", 0)
                if _public_ip_count>0:
                    for i in xrange(_public_ip_count):
                        _networkInfo.public_ips.add( parser.get("public_ips", ("public_ip_%s" % i)) )
                
                # read [allocated_ips] section
                _allocated_ip_count = config_parser_util.getint(parser, "DEFAULT", "allocated_ip_count", 0)
                if _allocated_ip_count>0:
                    for i in xrange(_allocated_ip_count):
                        _networkInfo.allocated_ips.add( parser.get("allocated_ips", ("allocated_ip_%s" % i)) )
                
                # read [bound_ports] section
                _bound_ports_count = config_parser_util.getint(parser, "DEFAULT", "bound_ports_count", 0)
                if _bound_ports_count>0:
                    for i in xrange(_bound_ports_count):
                        _entry = parser.get("bound_ports", ("bound_port_%s" % i))
                        _entry_arr = _entry.split("->")
                        _networkInfo.bound_ports[_entry_arr[0]] = _entry_arr[1]
                
                self.network_info[network_id] = _networkInfo
                
            self.logger.info("<network_manager> %d network(s) loaded in '%s'" % (network_count, list_file))
            return True

    def containsNetwork(self, uuid):
        with self._lock:
            return self.network_info.has_key(uuid)
    
    def getNetwork(self, network_id):
        with self._lock:
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                return None
            else:
                return _networkInfo

    
    def getAllNetworks(self):
        with self._lock:
            _result = []
            # instance of NetworkInfo
            for _networkInfo in self.network_info.values():
                _result.append(_networkInfo)
            return _result
            
    
    def createNetwork(self, networkInfo):
        with self._lock:
            if not isinstance(networkInfo.netmask, (int, long)) or networkInfo.netmask>32:
                self.logger.error("<network_manager> create network fail, wrong value of property netmask '%s'" % networkInfo.netmask)
                return False
                
            # _new_item: (int_begin_ip, int_end_ip, netmask, str_begin_ip, str_end_ip)
            _new_item = self._generateNetworkItem(networkInfo.netmask)
            if _new_item[0] > self._max_ip:
                self.logger.error("<network_manager> create network fail, not enough ip resource")
                return False
            
            self.network_resource[_new_item[0]] = _new_item
            self.is_sorted = False
            
            networkInfo.uuid = uuid.uuid4().hex
            networkInfo.network_address   = _new_item[3]
            networkInfo.netmask           = _new_item[2]
            networkInfo.broadcast_address = _new_item[4]
            self.network_info[networkInfo.uuid] = networkInfo
            
            self.logger.info("<network_manager> create network success, network '%s'('%s')" % (networkInfo.name, networkInfo.uuid))
            
            self.saveNetworkList()
            self.saveNetworkInfo(networkInfo.uuid)
            return True
        
    
    def deleteNetwork(self, network_id):
        with self._lock:
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> delete network fail, invalid network id '%s'" % network_id)
                return False
            
            self.deleteNetworkResource(_networkInfo.network_address, _networkInfo.netmask)
            del self.network_info[network_id]
            
            self.deleteNetworkPath(network_id)
            
            self.logger.info("<network_manager> delete network success")
            
            self.saveNetworkList()
            
            return True
            
    
    def sortResource(self):
        with self._lock:
            if self.is_sorted == False:
                
                _sorted_items = sorted(self.network_resource.items())
                self.network_resource = OrderedDict()
                
                for _resource in _sorted_items:
                    self.network_resource[_resource[0]] = _resource[1]
                    
                self.is_sorted = True
    
    
    # return: (int_begin_ip, int_end_ip, netmask, str_begin_ip, str_end_ip)
    def _generateNetworkItem(self, netmask):
        int_hostmask = 2 ** (32 - netmask) - 1
        with self._lock:
            self.sortResource()
            
            _last_int_end_ip = self._min_ip - 1
            
            for _resource in self.network_resource.values():
                _int_begin_ip = _resource[0]
                _int_end_ip   = _resource[1]
                
                if (_int_begin_ip - 1 - _last_int_end_ip) >= int_hostmask:
                    return (_last_int_end_ip + 1, 
                            _last_int_end_ip + 1 + int_hostmask, 
                            netmask, 
                            socket_util.convertIntToAddress(_last_int_end_ip + 1), 
                            socket_util.convertIntToAddress(_last_int_end_ip + 1 + int_hostmask))
                else:
                    _last_int_end_ip = _int_end_ip
                
            return (_last_int_end_ip + 1, 
                    _last_int_end_ip + 1 + int_hostmask, 
                    netmask, 
                    socket_util.convertIntToAddress(_last_int_end_ip + 1), 
                    socket_util.convertIntToAddress(_last_int_end_ip + 1 + int_hostmask))
        
    
    def deleteNetworkResource(self, str_ip, netmask):
        _int_ip = socket_util.convertAddressToInt(str_ip)
        with self._lock:
            self.sortResource()
            
            if not self.network_resource.has_key(_int_ip):
                self.logger.error("<network_manager> delete network resource '%s/%s' fail, invalid ip '%s'" % (str_ip, netmask, str_ip))
                return False
            
            _resource = self.network_resource[_int_ip]
            if _resource[2]!=netmask:
                self.logger.error("<network_manager> delete network resource '%s/%s' fail, invalid netmask '%s'" % (str_ip, netmask, netmask))
                return False
                
            del self.network_resource[_int_ip]
            self.logger.error("<network_manager> delete network resource '%s/%s' success" % (str_ip, netmask))
            return True
            
        
    
    def putNetwork(self, networkInfo):
        if networkInfo.uuid==None or not isinstance(networkInfo.uuid, str):
            self.logger.info("<network_manager> put network fail, network '%s'('%s')" % (networkInfo.name, networkInfo.uuid))
            return False
        with self._lock:
            self.network_info[networkInfo.uuid] = networkInfo
            self.logger.info("<network_manager> put network success, network '%s'('%s')" % (networkInfo.name, networkInfo.uuid))
            self.saveNetworkList()
            self.saveNetworkInfo(networkInfo.uuid)
            return True
        
    
    def saveNetworkList(self):
        with self._lock:
            parser = ConfigParser()
            data_count = len(self.network_info)
            parser.set("DEFAULT", "data_count", data_count)   
                 
            index = 0
            for data in self.network_info.values():
                parser.set("DEFAULT", "uuid_%d"%(index), data.uuid)              
                index += 1

            _network_conclusion_file = os.path.join(self.pool_path, "network_list.info")
            with io.open(_network_conclusion_file, "wb") as _file:
                parser.write(_file)
                self.logger.info("<network_manager> %d network info saved into '%s'"%(data_count, _network_conclusion_file))
                
            return True
        
    def deleteNetworkPath(self, network_id):
        _path = os.path.join(self.pool_path, network_id)
        if os.path.exists(_path):
            self.logger.info("<network_manager> delete network info dir '%s'" % (_path))
            os.remove(os.path.join(_path, "network_info.info"))
            os.rmdir(_path)
            return True
            
    
    def saveNetworkInfo(self, network_id):
        with self._lock:
            
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> save network info fail, invalid network id '%s'"%(network_id))
                return False
            
            # about network info
            parser = ConfigParser()   
            parser.set("DEFAULT", "uuid",              _networkInfo.uuid)     
            parser.set("DEFAULT", "name",              _networkInfo.name)       
            parser.set("DEFAULT", "network_address",   _networkInfo.network_address)         
            parser.set("DEFAULT", "netmask",           _networkInfo.netmask)       
            parser.set("DEFAULT", "broadcast_address", _networkInfo.broadcast_address) 
            parser.set("DEFAULT", "size",              _networkInfo.size)        
            parser.set("DEFAULT", "description",       _networkInfo.description)        
            parser.set("DEFAULT", "pool",              _networkInfo.pool)        
            parser.set("DEFAULT", "status",            _networkInfo.status)
            
            # about attached host info
            _host_count = len(_networkInfo.hosts)
            parser.set("DEFAULT", "host_count",  _host_count)
            
            if _host_count > 0:
                parser.add_section("hosts")
                i = 0
                for host_uuid in _networkInfo.hosts:
                    parser.set("hosts", ("host_%s" % i),  host_uuid)
                    i += 1
                    
            # about public ips 
            _public_ip_count = len(_networkInfo.public_ips)
            parser.set("DEFAULT", "public_ip_count",  _public_ip_count)
            
            if len(_networkInfo.public_ips)>0:
                parser.add_section("public_ips")
                i = 0
                for _ip in _networkInfo.public_ips:
                    parser.set("public_ips", ("public_ip_%s" % i),  _ip)
                    i += 1
            
            # about allocated ips 
            _allocated_ip_count = len(_networkInfo.allocated_ips)
            parser.set("DEFAULT", "allocated_ip_count",  _allocated_ip_count)
            
            if len(_networkInfo.allocated_ips)>0:
                parser.add_section("allocated_ips")
                i = 0
                for _ip in _networkInfo.allocated_ips:
                    parser.set("allocated_ips", ("allocated_ip_%s" % i),  _ip)
                    i += 1
                    
            # 
            _bound_ports_count = len(_networkInfo.bound_ports)
            parser.set("DEFAULT", "bound_ports_count",  _bound_ports_count)
            
            if len(_networkInfo.bound_ports)>0:
                parser.add_section("bound_ports")
                i = 0
                for _bound_port_entry in _networkInfo.bound_ports.items():
                    parser.set("bound_ports", ("bound_port_%s" % i),  "%s->%s" % (_bound_port_entry[0], _bound_port_entry[1]))
                    i += 1
            
            # save info filesystem
            path = os.path.join(self.pool_path, _networkInfo.uuid)
            if not os.path.exists(path):
                os.mkdir(path)
            
            network_info_file = os.path.join(path, "network_info.info")
            with io.open(network_info_file, "wb") as _file:
                parser.write(_file)
                self.logger.info("<network_manager> network '%s' saved into '%s'"%(_networkInfo.name, network_info_file))
                
            return True
        
        
        
    def startNetwork(self, network_id):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> save network info fail, invalid network id '%s'"%(network_id))
                return False
            
            self.logger.info("<network_manager> start network success, network '%s'('%s')" % (_networkInfo.name, _networkInfo.uuid))
            return True
        
        
    def stopNetwork(self, network_id):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> stop network info fail, invalid network id '%s'"%(network_id))
                return False
            
            self.logger.info("<network_manager> stop network success, network '%s'('%s')" % (_networkInfo.name, _networkInfo.uuid))
            return True
        
        
    def attachHost(self, network_id, host_id, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network attach host fail, invalid network id '%s'"%(network_id))
                return False
            
            _networkInfo.hosts.add(host_id)
            
            if save:
                self.saveNetworkInfo(network_id);
            
            self.logger.info("<network_manager> network '%s' attach host '%s' success"%(network_id, host_id))
            return True
        
        
    def detachHost(self, network_id, host_id, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network detach host fail, invalid network id '%s'"%(network_id))
                return False
            
            try:
                _networkInfo.hosts.remove(host_id)
                if save:
                    self.saveNetworkInfo(network_id)
                return True
            except KeyError:
                return False
            
            
    def attachAddress(self, network_id, ips, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network attach host address, invalid network id '%s'"%(network_id))
                return False
            
            for _ip in ips:
                _networkInfo.public_ips.add(_ip)
                
            if save:
                self.saveNetworkInfo(network_id);
            
            self.logger.info("<network_manager> network '%s' attach adress %s success"%(network_id, ips))
            return True
        
        
    def detachAddress(self, network_id, ips, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network detach host address, invalid network id '%s'"%(network_id))
                return False
            
            for _ip in ips:
                _networkInfo.public_ips.discard(_ip)
                
            if save:
                self.saveNetworkInfo(network_id);
            
            self.logger.info("<network_manager> network '%s' detach adress %s success"%(network_id, ips))
            return True
        
        
    def allocateIp(self, network_id, count, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network allocate ip address, invalid network id '%s'"%(network_id))
                return False
        
            if save:
                self.saveNetworkInfo(network_id);
            
            return _networkInfo.allocateIp(count)
        
    
    def deallocateIp(self, network_id, ip, save=True):
        with self._lock:
                
            _networkInfo = self.network_info.get(network_id, None)
            if _networkInfo==None:
                self.logger.error("<network_manager> network deallocate ip address, invalid network id '%s'"%(network_id))
                return False
            
            if save:
                self.saveNetworkInfo(network_id);
            
            return _networkInfo.deallocateIp(ip)
        
    def containAddressPool(self, address_pool):
        if len(strip(address_pool)) != 0:
            with self._lock:
                for network in self.network_info.values():
                    pool = network.pool
                    if len(strip(pool)) != 0 and pool == address_pool:
                        return True
                    
        return False


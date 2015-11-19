#!/usr/bin/python
import logging
import threading
import uuid
import os.path
import io
import struct
import zlib
from common import json_util, config_parser_util
from ConfigParser import ConfigParser, NoOptionError
from host_forwarder import HostForwarder, ForwarderPort, ForwarderTypeEnum

class ForwarderManager(object):
    
    def __init__(self, resource_path, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.config_file = os.path.join(resource_path, "forwarder.ini")

        ##key = uuid, value = HostForwarder
        self.forwarder = {}
        self.modified = False
        self.lock = threading.RLock()
        self.crc = 0


    def save(self):
        with self.lock:
            
            if not self.modified:
                return True
            
            parser = ConfigParser()
            data_count = len(self.forwarder)
            
            # write DEFAULT section
            parser.set("DEFAULT", "data_count", data_count)        
            index = 0
            for hostForwarder in self.forwarder.values():
                
                # write forwarder_%d section
                section = "forwarder_%d"%(index)
                parser.add_section(section)
                parser.set(section, "uuid", hostForwarder.uuid)
                parser.set(section, "type", hostForwarder.type)
                
                if 0 == len(hostForwarder.public_ip):
                    parser.set(section, "public_ip", "")
                else:
                    parser.set(section, "public_ip", ",".join(hostForwarder.public_ip))

                parser.set(section, "host_id",        hostForwarder.host_id)
                parser.set(section, "host_name",      hostForwarder.host_name)
                parser.set(section, "vpc_range",      hostForwarder.vpc_range)
                parser.set(section, "vpc_ip",         hostForwarder.vpc_ip)
                parser.set(section, "server_ip",      hostForwarder.server_ip)
                parser.set(section, "server_monitor", hostForwarder.server_monitor)
                parser.set(section, "public_monitor", hostForwarder.public_monitor)
                
                # port
                port_arr = hostForwarder.port
                port_count = len(port_arr)
                parser.set(section, "port_count", port_count)
                for i in xrange(port_count):
                    parser.set(section, ("port_%s" % i), str(port_arr[i].toJSONString()))
                    
#                 if 0 == len(hostForwarder.port):
#                     parser.set(section, "port", "")
#                 else:
#                     port_list = []
#                     for forward_port in hostForwarder.port:
#                         port_list.extend([str(forward_port.server_port),
#                                           str(forward_port.public_port),
#                                           str(forward_port.host_port)])
#                     parser.set(section, "port", ",".join(port_list))
                    
                # output_port_range
                if len(hostForwarder.output_port_range)==0:
                    parser.set(section, "output_port_range", "")
                else:
                    parser.set(section, "output_port_range", "%s-%s" % (hostForwarder.output_port_range[0], hostForwarder.output_port_range[1]))
                    
                parser.set(section, "enable", hostForwarder.enable)
                
                index += 1

            with io.open(self.config_file, "wb") as storage:
                parser.write(storage)
                self.logger.info("<ForwarderManager> %d forwarders saved into '%s'"%(data_count, self.config_file))
                
            self.modified = False
            
            
    def setSaveFlag(self):
        self.modified = True


    def load(self):
        with self.lock:
            
            if not os.path.exists(self.config_file):
                return False
            
            self.forwarder = {}
            parser = ConfigParser()
            
            # read file 'forwarder.ini'
            parser.read(self.config_file)
            
            # read section 'DEFAULT'
            data_count = parser.getint("DEFAULT", "data_count")
            for index in range(data_count):
                
                # read section 'forwarder_%d'
                section = "forwarder_%d" % (index)
                
                forwarder = HostForwarder()
                
                forwarder.uuid = parser.get(section,    "uuid")
                forwarder.type = parser.getint(section, "type")
                
                ip_value = parser.get(section, "public_ip").strip()      
                if 0 != len(ip_value):
                    forwarder.public_ip = ip_value.split(",")
                    
                forwarder.host_id        = config_parser_util.get(parser, section,    "host_id")
                forwarder.host_name      = config_parser_util.get(parser, section,    "host_name")
                forwarder.vpc_range      = config_parser_util.get(parser, section,    "vpc_range", "")
                forwarder.vpc_ip         = config_parser_util.get(parser, section,    "vpc_ip", "")
                forwarder.server_ip      = config_parser_util.get(parser, section,    "server_ip")
                forwarder.server_monitor = config_parser_util.getint(parser, section, "server_monitor")
                forwarder.public_monitor = config_parser_util.getint(parser, section, "public_monitor")
                
                ######################################
                # just for bug fix
                if forwarder.vpc_range=="None":
                    forwarder.vpc_range = ""
                
                if forwarder.vpc_ip=="None":
                    forwarder.vpc_ip = ""
                #######################################
                
                # port
                port_count = config_parser_util.getint(parser, section, "port_count", None)
                if port_count!=None:
                    for i in xrange(port_count):
                        _port_json = config_parser_util.get(parser, section, "port_%s" % i, None)
                        try:
                            _port_dict = eval(_port_json)
                        except:
                            _port_dict = json_util.parseToJson(_port_json)
                        port = ForwarderPort()
                        port.protocol    = _port_dict["protocol"]
                        port.public_ip   = _port_dict["public_ip"]
                        port.public_port = _port_dict["public_port"]
                        port.server_port = _port_dict["server_port"]
                        port.host_port   = _port_dict["host_port"]
                        forwarder.port.append(port)
                else:
                    port_value = parser.get(section, "port").strip()
                    if 0 != len(port_value):
                        port_list  = port_value.split(",")
                        port_count = len(port_list)
                        for offset in range(0, port_count, 3):
                            port = ForwarderPort()
                            port.server_port = int(port_list[offset])
                            port.public_port = int(port_list[offset + 1])
                            port.host_port   = int(port_list[offset + 2])
                            forwarder.port.append(port)
                          
                # output port range
                try:
                    _output_port_range = parser.get(section, "output_port_range").strip()
                    if bool(_output_port_range):
                        _output_port_range_arr = _output_port_range.split("-")
                        forwarder.output_port_range = [int(_output_port_range_arr[0]), int(_output_port_range_arr[1])]
                except NoOptionError:
                    forwarder.output_port_range = []

                forwarder.computeSignature()
                # forwarder.enable = parser.getboolean(section, "enable")
                forwarder.enable = False
                self.forwarder[forwarder.uuid] = forwarder
                
            self.updateTotalCRC()
            self.logger.info("<ForwarderManager> %d forwarders loaded from '%s'"%(data_count, self.config_file))
            
            return True            


    def create(self, hostForwarder):
        with self.lock:
            
            if 0 == len(hostForwarder.uuid):
                hostForwarder.uuid = uuid.uuid4().hex
                
            if self.forwarder.has_key(hostForwarder.uuid):
                self.logger.error("<ForwarderManager> create forwarder fail, id '%s' already exists"%(uuid))
                return False
            
            self.forwarder[hostForwarder.uuid] = hostForwarder
            ##update crc
            self.forwarder[hostForwarder.uuid].computeSignature()
            self.updateTotalCRC()
            self.logger.info("<ForwarderManager> forwarder '%s' created"%(hostForwarder.uuid))
            
            if not self.modified:
                self.modified = True
                
            return True

    # deprecated, please use modifyByDict()
    def modify(self, uuid, config):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return False
            current = self.forwarder[uuid]
            
            if 0 != len(config.host_id):
                current.host_id = config.host_id
                
            if 0 != len(config.host_name):
                current.host_name = config.host_name
                
            if 0 != len(config.server_ip):
                current.server_ip = config.server_ip
                
            if 0 != len(config.port):
                current.port = config.port
                
            if 0 != config.server_monitor:
                current.server_monitor = config.server_monitor
                
            ##update crc
            current.computeSignature()
            self.updateTotalCRC()
            self.logger.info("<ForwarderManager> forwarder '%s' modified"%(uuid))
            if not self.modified:
                self.modified = True
            return True
        
    
    def modifyByDict(self, uuid, forwarder_dict):
        with self.lock:
            
            if not self.forwarder.has_key(uuid):
                return False
            
            current = self.forwarder[uuid]
            
            if forwarder_dict.has_key("host_id"):
                current.host_id = forwarder_dict["host_id"]
                
            if forwarder_dict.has_key("host_name"):
                current.host_name = forwarder_dict["host_name"]
                
            if forwarder_dict.has_key("server_ip"):
                current.server_ip = forwarder_dict["server_ip"]
                
            if forwarder_dict.has_key("port"):
                current.port = forwarder_dict["port"]
                
            if forwarder_dict.has_key("server_monitor"):
                current.server_monitor = forwarder_dict["server_monitor"]
                
            ##update crc
            current.computeSignature()
            self.updateTotalCRC()
            
            self.logger.info("<ForwarderManager> forwarder '%s' modified"%(uuid))
            
            if not self.modified:
                self.modified = True
                
            return True
        
        
    def put(self, hostForwarder):
        with self.lock:
            
            if 0 == len(hostForwarder.uuid):
                hostForwarder.uuid = uuid.uuid4().hex
                
            if self.forwarder.has_key(hostForwarder.uuid):
                self.logger.info("<ForwarderManager> modify forwarder, id '%s'"%(hostForwarder.uuid))
            else:
                self.logger.info("<ForwarderManager> add forwarder, id '%s'"%(hostForwarder.uuid))
            
            self.forwarder[hostForwarder.uuid] = hostForwarder
            
            ##update crc
            self.forwarder[hostForwarder.uuid].computeSignature()
            self.updateTotalCRC()
            
            if not self.modified:
                self.modified = True
                
            return True
        
    def isInvalid(self, uuid):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return True
            current = self.forwarder[uuid]
            if 0 == len(current.host_id):
                return True
            return False

    def delete(self, uuid):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return False
            
            self.logger.info("<ForwarderManager> forwarder '%s' deleted"%(uuid))
            del self.forwarder[uuid]
            
            self.updateTotalCRC()
            if not self.modified:
                self.modified = True
            return True
        
    def updateTotalCRC(self):        
        with self.lock:
            crc_list = []
            for forwarder in self.forwarder.values():
                if forwarder.enable:
                    crc_list.append(forwarder.crc)
            crc_list.sort()
            data = ""
            for crc in crc_list:
                data += struct.pack(">I", crc)
            self.crc = zlib.crc32(data)&0xffffffff

    def getCRC(self):
        return self.crc

    def contains(self, uuid):
        with self.lock:
            return self.forwarder.has_key(uuid)

    def get(self, uuid, copy=False):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return None
            else:
                if copy:
                    return self.forwarder[uuid].copy()
                else:
                    return self.forwarder[uuid]

    def query(self, forwarder_type):
        """
        query by type
        """
        with self.lock:
            result = []
            for forwarder in self.forwarder.values():
                if (forwarder.type == forwarder_type) and (forwarder.enable):
                    ##only return enabled forwarder
                    result.append(forwarder)
            return result
        
    def getAllCRC(self):
        with self.lock:
            id_list = []
            crc_list = []
            for forwarder in self.forwarder.values():
                if forwarder.enable:
                    id_list.append(forwarder.uuid)
                    crc_list.append(forwarder.crc)
            return id_list, crc_list

    def statistic(self):
        """
        @return: mono_enabled, mono_total, share_enabled, share_total
        """
        with self.lock:
            mono_enabled = 0
            mono_total = 0
            share_enabled = 0
            share_total = 0
            for forwarder in self.forwarder.values():
                if ForwarderTypeEnum.mono == forwarder.type:
                    mono_total += 1
                    if forwarder.enable:
                        mono_enabled += 1
                else:
                    share_total += 1
                    if forwarder.enable:
                        share_enabled += 1

            return mono_enabled, mono_total, share_enabled, share_total  

    def enable(self, uuid):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return False
            forwarder = self.forwarder[uuid]
            forwarder.enable = True
            self.updateTotalCRC()
            self.logger.info("<ForwarderManager> forwarder '%s' enabled"%(
                uuid))
            if not self.modified:
                self.modified = True
            return True

    def disable(self, uuid):
        with self.lock:
            if not self.forwarder.has_key(uuid):
                return False
            forwarder = self.forwarder[uuid]
            forwarder.enable = False
            self.updateTotalCRC()
            self.logger.info("<ForwarderManager> forwarder '%s' disabled"%(uuid))
            if not self.modified:
                self.modified = True
            return True
    

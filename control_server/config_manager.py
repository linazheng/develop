#!/usr/bin/python
import logging
import threading

class ConfigManager(object):  
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        ##key = uuid, value = server room info
        self.server_rooms = {}
        ##key = uuid, value = server rack info
        self.server_racks = {}
        ##key = uuid, value = server info
        self.servers = {}
        ##key = uuid, value = HostInfo
        self.hosts = {}
        ##key = room id, value = list of rack id
        self.room_members = {}
        ##key = rack id, value = list of server id
        self.rack_members = {}
        ##key = service name, value = list of host id
        self.host_in_service = {}
        ##key = session id, value = host info
        self.host_in_creating = {}
        self.lock = threading.RLock()

    def loadServerRooms(self, room_list):
        with self.lock:
            self.server_rooms = {}
            self.room_members = {}
            for server_room in room_list:
                self.server_rooms[server_room.uuid] = server_room
            self.logger.info("<ConfigManager> %d server room(s) loaded"%(
                len(room_list)))
            return True
        
    def loadServerRacks(self, room_id, rack_list):
        with self.lock:
            if self.room_members.has_key(room_id):
                ##clear all
                for rack_id in self.room_members[room_id]:
                    del self.server_racks[rack_id]
                del self.room_members[room_id]

            self.room_members[room_id] = []
            for rack in rack_list:
                self.server_racks[rack.uuid] = rack
                self.room_members[room_id].append(rack.uuid)
                    
            self.logger.info("<ConfigManager> %d server rack(s) loaded for server room '%s'"%(
                len(rack_list), room_id))
            return True

    def loadServers(self, rack_id, server_list):
        with self.lock:
            if self.rack_members.has_key(rack_id):
                ##clear all
                for server_id in self.rack_members[rack_id]:
                    del self.servers[server_id]
                del self.rack_members[rack_id]

            self.rack_members[rack_id] = []
            for server in server_list:
                self.servers[server.uuid] = server
                self.rack_members[rack_id].append(server.uuid)
                    
            self.logger.info("<ConfigManager> %d server(s) loaded for server rack '%s'"%(
                len(server_list), rack_id))
            return True
                
    def containsServerRoom(self, room_id):
        with self.lock:
            return (self.server_rooms.has_key(room_id))

    def containsServerRack(self, rack_id):
        with self.lock:
            return (self.server_racks.has_key(rack_id))

    def containsServer(self, server_id):
        with self.lock:
            return (self.servers.has_key(server_id))

    def queryAllServerRooms(self):
        with self.lock:
            return self.server_rooms.values()

    def queryServerRacks(self, room_id):
        with self.lock:
            result = []
            if not self.room_members.has_key(room_id):
                return result
            for rack_id in self.room_members[room_id]:
                if self.server_racks.has_key(rack_id):
                    result.append(self.server_racks[rack_id])
            return result
        
    def getServerRack(self, rack_id):
        with self.lock:
            if self.server_racks.has_key(rack_id):
                return self.server_racks[rack_id]
            
            return None

    def queryServers(self, rack_id):
        with self.lock:
            result = []
            if not self.rack_members.has_key(rack_id):
                return result
            for server_id in self.rack_members[rack_id]:
                if self.servers.has_key(server_id):
                    result.append(self.servers[server_id])
            return result
        
    def getServer(self, server_id):
        with self.lock:
            if self.servers.has_key(server_id):
                return self.servers[server_id]
            
            return None
    
    def addServerRoom(self, info):
        with self.lock:
            if self.server_rooms.has_key(info.uuid):
                self.logger.error("<ConfigManager> add server room fail, server room '%s' already exist"%info.name)
                return False
            ##new room
            self.server_rooms[info.uuid] = info
            self.logger.info("<ConfigManager> add server room success, name '%s'(uuid '%s')"%
                             (info.name, info.uuid))
            return True
    
    def removeServerRoom(self, uuid):
        with self.lock:
            if not self.server_rooms.has_key(uuid):
                self.logger.error("<ConfigManager> remove server room fail, invalid id '%s'"%
                                  uuid)
                return False
            server_room = self.server_rooms[uuid]
            if self.room_members.has_key(uuid):
                self.logger.error("<ConfigManager> remove server room fail, still has members in server room '%s'"%
                                  (server_room.name))
                return False            
            ##remove room
            self.logger.info("<ConfigManager> remove server room success, server room '%s'('%s')"%(
                server_room.name, server_room.uuid))
            del self.server_rooms[uuid]        
            return True

    def modifyServerRoom(self, uuid, info):
        with self.lock:
            if not self.server_rooms.has_key(uuid):
                self.logger.error("<ConfigManager> modify server room fail, invalid id '%s'"%
                                  uuid)
                return False
            server_room = self.server_rooms[uuid]
            server_room.name = info.name
            server_room.domain = info.domain
            server_room.display_name = info.display_name
            server_room.description = info.description
            self.logger.info("<ConfigManager> modify server room success, server room '%s'('%s')"%(
                server_room.name, server_room.uuid))
            return True

    def addServerRack(self, info):
        with self.lock:
            if self.server_racks.has_key(info.uuid):
                self.logger.error("<ConfigManager> add server rack fail, rack '%s' already exist"%
                           info.uuid)
                return False
            ##new computer rack
            self.server_racks[info.uuid] = info
            server_id = info.server_room
            if not self.room_members.has_key(server_id):
                self.room_members[server_id] = [info.uuid]
            else:
                self.room_members[server_id].append(info.uuid)
            self.logger.info("<ConfigManager> add server rack success, rack '%s'('%s')"%(
                info.name, info.uuid))
            return True
    
    def removeServerRack(self, rack_id):
        with self.lock:
            if not self.server_racks.has_key(rack_id):
                self.logger.error("<ConfigManager> remove server rack fail, invalid id '%s'"%
                           rack_id)
                return False        
            if self.rack_members.has_key(rack_id):
                self.logger.error("<ConfigManager> remove server rack fail, still has members in rack '%s'"%
                           rack_id)
                return False
            
            server_id = self.server_racks[rack_id].server_room
            ##room member
            if self.room_members.has_key(server_id):
                rack_list = self.room_members[server_id]
                if rack_id in rack_list:
                    del rack_list[rack_list.index(rack_id)]
                    
                if 0 == len(rack_list):
                    del self.room_members[server_id]                    
            rack = self.server_racks[rack_id]
            ##remove rack
            self.logger.info("<ConfigManage>remove server rack success, rack '%s'('%s')"%
                             (rack.name, rack.uuid))
            del self.server_racks[rack_id]        
            return True

    def modifyServerRack(self, uuid, info):
        with self.lock:
            if not self.server_racks.has_key(uuid):
                self.logger.error("<ConfigManager> modify server rack fail, invalid id '%s'"%
                           uuid)
                return False
            rack = self.server_racks[uuid]
            rack.name = info.name
            rack.server_room = info.server_room
            self.logger.info("<ConfigManager> modify server rack success, server rack '%s'('%s')"%(
                rack.name, rack.uuid))
            return True

    def addServer(self, info):
        with self.lock:
            if self.servers.has_key(info.uuid):
                self.logger.error("<ConfigManage>add server fail, server '%s' already exist"%
                           info.name)
                return False
            ##new node
            self.servers[info.uuid] = info
            rack_id = info.rack
            if not self.rack_members.has_key(rack_id):
                self.rack_members[rack_id] = [info.uuid]
            else:
                self.rack_members[rack_id].append(info.uuid)
            self.logger.info("<ConfigManage>add server success, server '%s'('%s')"%(
                info.name, info.uuid))
            return True
    
    def removeServer(self, server_id):
        with self.lock:
            if not self.servers.has_key(server_id):
                self.logger.error("<ConfigManage>remove server fail, invalid id '%s'"%
                           server_id)
                return False
            server = self.servers[server_id]
            rack_id = server.rack
            ##rack member
            if self.rack_members.has_key(rack_id):
                server_list = self.rack_members[rack_id]
                if server_id in server_list:
                    del server_list[server_list.index(server_id)]
                    
                if 0 == len(server_list):
                    del self.rack_members[rack_id]                
            
            ##remove server
            self.logger.info("<ConfigManage>remove server success, server '%s'('%s')"%
                             (server.name, server.uuid))
            del self.servers[server_id]
            return True

    def modifyServer(self, uuid, info):
        with self.lock:
            if not self.servers.has_key(uuid):
                self.logger.error("<ConfigManage>modify server fail, invalid id '%s'"%
                           uuid)
                return False
            server = self.servers[uuid]
            server.rack = info.rack
            server.name = info.name
            self.logger.info("<ConfigManage>modify server success, server '%s'('%s')"%
                             (server.name, server.uuid))
            return True

    """
    hosts
    @service_name: node client name
    """
    def loadHosts(self, service_name, host_list):
        with self.lock:
            if self.host_in_service.has_key(service_name):
                ##clear all
                for host_id in self.host_in_service[service_name]:
                    del self.hosts[host_id]
                del self.host_in_service[service_name]

            self.host_in_service[service_name] = []
            for host in host_list:
                host.container = service_name
                self.hosts[host.uuid] = host
                self.host_in_service[service_name].append(host.uuid)

            self.logger.info("<ConfigManager> %d host(s) loaded in container '%s'"%(len(host_list), service_name))
            return True                                              

    def addHost(self, info):
        with self.lock:
            
            if self.hosts.has_key(info.uuid):
                self.logger.error("<ConfigManager> add host fail, host '%s' already exist" % info.uuid)
                return False
            
            ##new node
            self.hosts[info.uuid] = info
            service_name = info.container
            
            if not self.host_in_service.has_key(service_name):
                self.host_in_service[service_name] = [info.uuid]
            else:
                self.host_in_service[service_name].append(info.uuid)
                
            self.logger.info("<ConfigManager> add host success, host '%s'('%s')"%(info.name, info.uuid))
            return True
        
    
    def modifyHost(self, uuid, host_dict):
        with self.lock:
            
            host = self.hosts.get(uuid, None)
            if host==None:
                self.logger.error("<ConfigManager> modify host fail, invalid uuid '%s'" % uuid)
                return False
            
            if host_dict.has_key("vpc_ip"):
                host.vpc_ip = host_dict["vpc_ip"]
                
            if host_dict.has_key("forwarder"):
                host.forwarder = host_dict["forwarder"]
                
            if host_dict.has_key("public_ip"):
                host.public_ip = host_dict["public_ip"]
                
            if host_dict.has_key("public_port"):
                host.public_port = host_dict["public_port"]
                
            if host_dict.has_key("port"):
                host.port = host_dict["port"]
                
            if host_dict.has_key("network"):
                host.network = host_dict["network"]
                
            self.logger.info("<ConfigManager> modify host '%s' success" % (uuid))
            return True
        

    def removeHost(self, uuid):
        with self.lock:
            if not self.hosts.has_key(uuid):
                self.logger.error("<ConfigManager> remove host fail, invalid id '%s'"%uuid)
                return False
            
            host = self.hosts[uuid]
            service_name = host.container
                                                          
            if self.host_in_service.has_key(service_name):
                host_list = self.host_in_service[service_name]
                if uuid in host_list:
                    del host_list[host_list.index(uuid)]
                    
                if 0 == len(host_list):
                    del self.host_in_service[service_name]                
            
            ##remove host
            self.logger.info("<ConfigManager> remove host success, host '%s'('%s')"%
                             (host.name, host.uuid))
            del self.hosts[uuid]
            return True

    def updateHost(self, info):
        with self.lock:
            if not self.hosts.has_key(info.uuid):
                self.logger.error("<ConfigManager> update host fail, host '%s' does not exist" % info.uuid)
                return False
            
            ##new node
            self.hosts[info.uuid] = info
            service_name = info.container
            
            if not self.host_in_service.has_key(service_name):
                self.host_in_service[service_name] = [info.uuid]
                
            self.logger.debug("<ConfigManager> update host success, host '%s'('%s')"%(info.name, info.uuid))
            return True

    def getHost(self, uuid):
        with self.lock:
            if self.hosts.has_key(uuid):
                return self.hosts[uuid]
            else:
                return None


    def containsHost(self, uuid):
        with self.lock:
            return self.hosts.has_key(uuid)


    def queryHosts(self, service_name):                                                      
        with self.lock:
            result = []
            if not self.host_in_service.has_key(service_name):
                return result
            for uuid in self.host_in_service[service_name]:
                if self.hosts.has_key(uuid):
                    result.append(self.hosts[uuid])
            return result    

    def addCreatingHost(self, session_id, host_info):
        with self.lock:
            self.host_in_creating[session_id] = host_info
            
            return True
            
    def removeCreatingHost(self, session_id):
        with self.lock:
            host_info = self.host_in_creating.pop(session_id, None)
            return host_info
            
#             if self.host_in_creating.has_key(session_id):
#                 del self.host_in_creating[session_id]
#             return True
        
    def getAllCreatingHost(self):
        with self.lock:
            result = []
            for host_info in self.host_in_creating.values():
                result.append(host_info)
                
            return result
        

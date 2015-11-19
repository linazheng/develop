#!/usr/bin/python
import datetime
import logging
import threading
from server_status import *
from host_status import *

class StatusManager(object):
    max_timeout = 24
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        ##key = room id, value = server room status
        self.server_room_status = {}
        ##key = room id, value = counter
        self.server_room_counter = {}

        ##key = rack id, value = server rack status
        self.server_rack_status = {}
        ##key = rack id, value = counter
        self.server_rack_counter = {}
        
        ##key = uuid, value = server status
        self.server_status = {}
        ##key = uuid, value = counter
        self.server_counter = {}
        
        ##key = uuid, value = host status
        self.host_status = {}
        ##key = uuid, value = counter
        self.host_counter = {}

        ##key = uuid, value = compute pool status
        self.compute_pool_status = {}
        ##key = uuid, value = counter
        self.compute_pool_counter = {}

        self.system_status = None
        self.lock = threading.RLock()
        
    def checkTimeout(self):
        with self.lock:
            ##server room
            remove_list = []
            for room_id in self.server_room_counter.keys():
                self.server_room_counter[room_id] += 1
                if self.server_room_counter[room_id] > self.max_timeout:
                    remove_list.append(room_id)

            if 0 != len(remove_list):
                for room_id in remove_list:
                    if self.server_room_status.has_key(room_id):
                        del self.server_room_status[room_id]
                    if self.server_room_counter.has_key(room_id):
                        del self.server_room_counter[room_id]
                    self.logger.info("<status_manager> server room status timeout, id '%s'"%(room_id))

            ##server rack
            remove_list = []
            for rack_id in self.server_rack_counter.keys():
                self.server_rack_counter[rack_id] += 1
                if self.server_rack_counter[rack_id] > self.max_timeout:
                    remove_list.append(rack_id)

            if 0 != len(remove_list):
                for room_id in remove_list:
                    if self.server_rack_status.has_key(rack_id):
                        del self.server_rack_status[rack_id]
                    if self.server_rack_counter.has_key(rack_id):
                        del self.server_rack_counter[rack_id]
                    self.logger.info("<status_manager> server rack status timeout, id '%s'"%(rack_id))

            ##server
            remove_list = []
            for server_id in self.server_counter.keys():
                self.server_counter[server_id] += 1
                if self.server_counter[server_id] > self.max_timeout:
                    remove_list.append(server_id)

            if 0 != len(remove_list):
                for server_id in remove_list:
                    if self.server_status.has_key(server_id):
                        del self.server_status[server_id]
                    if self.server_counter.has_key(server_id):
                        del self.server_counter[server_id]
                    self.logger.info("<status_manager> server status timeout, id'%s'"%(server_id))
            ##host
            remove_list = []
            for host_id in self.host_counter.keys():
                self.host_counter[host_id] += 1
                if self.host_counter[host_id] > self.max_timeout:
                    remove_list.append(host_id)

            if 0 != len(remove_list):
                for host_id in remove_list:
                    if self.host_status.has_key(host_id):
                        del self.host_status[host_id]
                    if self.host_counter.has_key(host_id):
                        del self.host_counter[host_id]
                    self.logger.info("<status_manager> host status timeout, id '%s'"%(host_id))

            ##compute pool
            remove_list = []
            for pool_id in self.compute_pool_counter.keys():
                self.compute_pool_counter[pool_id] += 1
                if self.compute_pool_counter[pool_id] > self.max_timeout:
                    remove_list.append(pool_id)

            if 0 != len(remove_list):
                for pool_id in remove_list:
                    if self.compute_pool_status.has_key(pool_id):
                        del self.compute_pool_status[pool_id]
                    if self.compute_pool_counter.has_key(pool_id):
                        del self.compute_pool_counter[pool_id]
                    self.logger.info("<status_manager> compute pool status timeout, pool '%s'"%(pool_id))
    

    def updateServerStatus(self, uuid, status):
        with self.lock:
            self.server_status[uuid] = status
            self.server_counter[uuid] = 0

    def updateHostStatus(self, status_list):
        with self.lock:
            for status in status_list:
                self.host_status[status.uuid] = status
                self.host_counter[status.uuid] = 0
    
    def containsServerStatus(self, uuid):
        with self.lock:
            return self.server_status.has_key(uuid)

    def containsHostStatus(self, uuid):
        with self.lock:
            return self.host_status.has_key(uuid)

    def getServerStatus(self, uuid):
        with self.lock:
            if self.server_status.has_key(uuid):
                return self.server_status[uuid]
            else:
                return None
            
    def removeServerStatus(self, uuid):
        with self.lock:
            if self.server_status.has_key(uuid):
                del self.server_status[uuid]
                return True
            
            return False

    def getHostStatus(self, uuid):
        with self.lock:
            if self.host_status.has_key(uuid):
                return self.host_status[uuid]
            else:
                return None
            
    def addHostStatus(self, status):
        with self.lock:
            if not self.host_status.has_key(status.uuid):
                self.host_status[status.uuid] = status
                return True
            
            return False
        
    def removeHostStatus(self, host_id):
        with self.lock:
            if self.host_status.has_key(host_id):
                del self.host_status[host_id]
                return True
            
            return False
        
    def changeHostStatus(self, host_id, status):
        with self.lock:
            if self.host_status.has_key(host_id):
                self.host_status[host_id].status = status
                return True
            
            return False

    def updateComputePoolStatus(self, status_list):
        with self.lock:
            for status in status_list:
                self.compute_pool_status[status.uuid] = status
                self.compute_pool_counter[status.uuid] = 0
                                    

    def containsComputePoolStatus(self, uuid):
        with self.lock:
            return self.compute_pool_status.has_key(uuid)

    def getComputePoolStatus(self, uuid):
        with self.lock:
            if self.compute_pool_status.has_key(uuid):
                return self.compute_pool_status[uuid]
            else:
                return None

    def getAllComputePoolStatus(self):
        with self.lock:
            result = []
            for pool in self.compute_pool_status.values():
                result.append(pool)
            return result
        
    def removeComputePoolStatus(self, uuid):
        with self.lock:
            if self.compute_pool_counter.has_key(uuid):
                del self.compute_pool_counter[uuid]
                
            if self.compute_pool_status.has_key(uuid):
                del self.compute_pool_status[uuid]
                return True
        
        return False

    def updateServerRoomStatus(self, status_list):
        with self.lock:
            for status in status_list:
                self.server_room_status[status.uuid] = status
                self.server_room_counter[status.uuid] = 0                                

    def containsServerRoomStatus(self, uuid):
        with self.lock:
            return self.server_room_status.has_key(uuid)

    def getServerRoomStatus(self, uuid):
        with self.lock:
            if self.server_room_status.has_key(uuid):
                return self.server_room_status[uuid]
            else:
                return None

    def getAllServerRoomStatus(self):
        with self.lock:
            result = []
            for status in self.server_room_status.values():
                result.append(status)
            return result

    def updateServerRackStatus(self, status_list):
        with self.lock:
            for status in status_list:
                self.server_rack_status[status.uuid] = status
                self.server_rack_counter[status.uuid] = 0                                

    def containsServerRackStatus(self, uuid):
        with self.lock:
            return self.server_rack_status.has_key(uuid)

    def getServerRackStatus(self, uuid):
        with self.lock:
            if self.server_rack_status.has_key(uuid):
                return self.server_rack_status[uuid]
            else:
                return None
            
    def getAllServerRackStatus(self):
        with self.lock:
            result = []
            for status in self.server_rack_status.values():
                result.append(status)

            return result

    def updateSystemStatus(self, status):
        with self.lock:
            self.system_status = status                               

    def containsSystemStatus(self):
        with self.lock:
            return (self.system_status is not None)

    def getSystemStatus(self):
        with self.lock:
            return self.system_status
        
    def statisticHostStatus(self):
        with self.lock:
            stop = 0
            warning = 0
            error = 0
            running = 0
            for host_status in self.host_status.values():
                if host_status.status == HostStatusEnum.status_stop:
                    stop += 1
                elif host_status.status == HostStatusEnum.status_warning:
                    warning += 1
                elif host_status.status == HostStatusEnum.status_error:
                    error += 1
                else:
                    running += 1
            return [stop, warning, error, running]

    def getAllServerStatus(self):
        with self.lock:
            result = []
            for status in self.server_status.values():
                result.append(status)
            return result

    def getAllHostStatus(self):
        with self.lock:
            result = []
            for status in self.host_status.values():
                result.append(status)
            return result
    
            
            

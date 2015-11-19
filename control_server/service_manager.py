#!/usr/bin/python
from service.message_define import *
from service_status import *
from whisper_service import *
import collections
import datetime
import io
import logging
import os.path
import threading
import random

class ServiceManager(object):
    """
    store domain node register info/status
    not thread safe
    """
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        # #type group list
        # #key = server type, value = {group:list of service name}
        self.server_groups = {}

        # #key = service name, value = service
        self.service_map = {}
        # #key = server uuid, value = [service name]
        self.service_in_server = {}
        # #key = service name, value = [whisper service]
        self.whispers = {}
        self.lock = threading.RLock()

    def activeService(self, service):
        with self.lock:
            if not self.service_map.has_key(service.name):
                # #new service
                # #add new service to group
                if not self.server_groups.has_key(service.type):
                    # #new service type
                    self.server_groups[service.type] = {"default":[service.name]}
                else:
                    self.server_groups[service.type]["default"].append(service.name)

                self.service_map[service.name] = service

                if not self.service_in_server.has_key(service.server):
                    self.service_in_server[service.server] = [service.name]
                else:
                    if service.name not in self.service_in_server[service.server]:
                        self.service_in_server[service.server].append(service.name)

                self.logger.info("<ServiceManager> add new service, service name '%s'" % (
                    service.name))

            current = self.service_map[service.name]
            current.ip = service.ip
            current.port = service.port
            current.version = service.version
            current.status = ServiceStatus.status_running
            current.server = service.server
    # #        self.logger.info("<ServiceManager> service actived, service name '%s'"%(
    # #            current.name))
            return True

    def deactiveService(self, name):
        with self.lock:

            if not self.service_map.has_key(name):
                self.logger.error("<ServiceManager> deactive service fail, invalid service '%s'" % (name))
                return False

            if self.containsWhisper(name):
                self.removeWhisper(name)

            service = self.service_map[name]
            service.status = ServiceStatus.status_stop
            self.logger.info("<ServiceManager> service deactived, service name '%s'" % (name))
            return True

# #    def modifyService(self, name, service):
# #        pass

    def containsService(self, service_name):
        with self.lock:
            return self.service_map.has_key(service_name)

    def getService(self, service_name):
        with self.lock:
            if not self.service_map.has_key(service_name):
                return None
            else:
                return self.service_map[service_name]

    def loadService(self, service_type, service_list):
        with self.lock:

            if self.server_groups.has_key(service_type):
                new_service_map = {}
                for service in service_list:
                    new_service_map[service.name] = service
                    
                # #clear all
                for name_list in self.server_groups[service_type].values():
                    for service_name in name_list:
                        # remove service name in service_in_server
                        if self.service_map.has_key(service_name):
                            server = self.service_map[service_name].server
                            if self.service_in_server.has_key(server):
                                if service_name in self.service_in_server[server]:
                                    self.service_in_server[server].remove(service_name)
                                    if len(self.service_in_server[server]) == 0:
                                        del self.service_in_server[server]
                        
                        ## copy disk type
                        if new_service_map.has_key(service_name):
                            new_service = new_service_map[service_name]
                            disk_type = self.service_map[service_name].disk_type
                            new_service.disk_type = disk_type
                        # remove service name in service_map
                        del self.service_map[service_name]

            self.server_groups[service_type] = {"default":[]}

            for service in service_list:
                ## copy disk type
                if self.service_map.has_key(service.name):
                    old_service = self.service_map[service.name]
                    service.disk_type = old_service.disk_type
                
                self.service_map[service.name] = service
                self.server_groups[service_type]["default"].append(service.name)

                if not self.service_in_server.has_key(service.server):
                    self.service_in_server[service.server] = [service.name]
                else:
                    if service.name not in self.service_in_server[service.server]:
                        self.service_in_server[service.server].append(service.name)

            self.logger.info("<ServiceManager> %d service(s) loaded for service type %d" % (
                len(service_list), service_type))
            return True

    def queryService(self, service_type, service_group):
        with self.lock:
            result = []
            if not self.server_groups.has_key(service_type):
                return result
            group_dict = self.server_groups[service_type]
            if not group_dict.has_key(service_group):
                return result
            for name in group_dict[service_group]:
                if not self.service_map.has_key(name):
                    continue

                result.append(self.service_map[name])

            return result
        
    def updateService(self, name, disk_type):
        with self.lock:
            if self.service_map.has_key(name):
                self.service_map[name].disk_type = disk_type
            else:
                service = ServiceStatus()
                service.name = name
                service.disk_type = disk_type
                self.service_map[service.name] = service

    def queryServicesInServer(self, server_id):
        with self.lock:
            result = []
            if self.service_in_server.has_key(server_id):
                for service_name in self.service_in_server[server_id]:
                    result.append(service_name)

            return result

    def getAllServiceType(self):
        with self.lock:
            return self.server_groups.keys()

    def queryServiceGroup(self, service_type):
        with self.lock:
            result = []
            if self.server_groups.has_key(service_type):
                result.extend(self.server_groups[service_type].keys())

            return result

    def updateWhisper(self, service_name, whisper_list):
        with self.lock:
            if not self.service_map.has_key(service_name):
                return False
            # # remove all
            self.whispers[service_name] = []
            service = self.service_map[service_name]
            for whisper in whisper_list:
                whisper.name = service_name
                whisper.type = service.type
                self.whispers[service_name].append(whisper)

            return True

    def removeWhisper(self, service_name):
        with self.lock:
            if self.whispers.has_key(service_name):
                del self.whispers[service_name]

    def getAllWhisper(self):
        with self.lock:
            result = []
            for whisper_list in self.whispers.values():
                result.extend(whisper_list)

            return result

    def containsWhisper(self, service_name):
        with self.lock:
            return (self.whispers.has_key(service_name))

    def getWhisper(self, service_name):
        with self.lock:
            if self.whispers.has_key(service_name):
                # #load balance
                whisper_list = self.whispers[service_name]
                index = random.randint(0, len(whisper_list) - 1)
                whisper = whisper_list[index]

                return whisper
            else:
                return None

    def statisticStatus(self):
        with self.lock:
            stop = 0
            warn = 0
            error = 0
            run = 0
            for service in self.service_map.values():
                if service.status == ServiceStatus.status_stop:
                    stop += 1
                elif service.status == ServiceStatus.status_warning:
                    warn += 1
                elif service.status == ServiceStatus.status_error:
                    error += 1
                else:
                    run += 1

            return [stop, warn, error, run]


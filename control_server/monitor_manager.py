#!/usr/bin/python
from service.logger_helper import *
from data.monitor_level import *

class Monitor(object):        
    level = 0
    listener_list = []
    global_listener = []
    target_map = {}
    def __init__(self, level):        
        self.level = level
        ##list of all task
        self.listener_list = []
        ##list of listen all 
        self.global_listener = []
        ##key = target id, value = list of task id
        self.target_map = {}
    

class MonitorTask(object):
    task_id = 0
    receive_node = ""
    receive_session = 0
    monitor_level = 0
    global_monitor = False
    target_list = None
    timeout_count = 0

class MonitorManager(LoggerHelper):
    task_id_seed = 0
    ##key = task id, value = task
    task_map = {}
    max_timeout = 5
    def __init__(self, logger_name):
        LoggerHelper.__init__(self, logger_name)
        self.task_map = {}
        system_monitor = Monitor(MonitorLevel.system)
        room_monitor = Monitor(MonitorLevel.server_room)
        rack_monitor = Monitor(MonitorLevel.server_rack)
        server_monitor = Monitor(MonitorLevel.server)
        compute_monitor = Monitor(MonitorLevel.compute_node)
        storage_monitor = Monitor(MonitorLevel.storage_node)
        host_monitor = Monitor(MonitorLevel.host)
        self.monitor_list = [system_monitor, room_monitor, rack_monitor,
                             compute_monitor, server_monitor, host_monitor]

    def addTask(self, task):
        self.task_id_seed += 1
        task.task_id = self.task_id_seed
        for monitor in self.monitor_list:
            if task.monitor_level == monitor.level:
                self.task_map[task.task_id] = task
                monitor.listener_list.append(task.task_id)
                if task.global_monitor:
                    monitor.global_listener.append(task.task_id)
                    self.debug("<monitor_manager> monitor %d:add global listener %d"%(
                        monitor.level, task.task_id))
                else:
                    ##add target
                    for target in task.target_list:
                        if monitor.target_map.has_key(target):
                            ##append listener
                            monitor.target_map[target].append(task.task_id)
                            self.debug("<monitor_manager> monitor %d:add listener %d for target '%s'"%(
                                monitor.level, task.task_id, target))
                        else:
                            ##new listener
                            monitor.target_map[target] = [task.task_id]
                            self.debug("<monitor_manager> monitor %d:new listener %d for target '%s'"%(
                                monitor.level, task.task_id, target))
                return True
        else:
            ##invalid level
            self.error("<monitor_manager> invalid monitor task level %d"%task.monitor_level)
            return False
        
    def getTask(self, task_id):
        return self.task_map[task_id]
    
    def removeTask(self, task_id):
        if self.task_map.has_key(task_id):
            task = self.task_map[task_id]
            for monitor in self.monitor_list:
                if monitor.level == task.monitor_level:
                    if task.global_monitor:
                        monitor.global_listener.remove(task.task_id)
                        self.debug("<monitor_manager> monitor %d removed global listener %d"%
                                   (monitor.level, task_id))
                    else:
                        for target in task.target_list:
                            monitor.target_map[target].remove(task.task_id)
                            self.debug("<monitor_manager> monitor %d removed listener %d for target '%s'"%
                                   (monitor.level, task_id, target))

                            if 0 == len(monitor.target_map[target]):
                                del monitor.target_map[target]
                                self.debug("<monitor_manager> monitor %d removed target '%s'"%
                                   (monitor.level, target))

                    monitor.listener_list.remove(task_id)
            del self.task_map[task_id]
            self.debug("<monitor_manager> task %d removed"%task_id)
            return True
        else:
            return False

    def getAllMonitor(self):
        return self.monitor_list
    
    def checkTimeout(self):
        clear = []
        for task in self.task_map.values():
            task.timeout_count += 1
            if task.timeout_count > self.max_timeout:
                clear.append(task.task_id)
                self.warn("<monitor_manager> task %d timeout"%task.task_id)
        if 0 != len(clear):
            for task_id in clear:
                self.removeTask(task_id)

    def processHeartBeat(self, task_id):
        if self.task_map.has_key(task_id):
            self.task_map[task_id].timeout_count = 0
        
    def isNodeMonitored(self, node_name):
        pass

    def getNodeMonitor(self, node_name):
        pass

    def isDomainMonitored(self, domain_name):
        pass
    
    def getDomainMonitor(self, domain_name):
        pass
    

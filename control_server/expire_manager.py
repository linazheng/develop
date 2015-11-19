#!/usr/bin/python
import threading

class ExpireManager(object):
    
    resource_type_host = 0
    
    expire_type_found = 0
    expire_type_lost = 1
    
    def __init__(self):
        self.lock = threading.RLock()
        ##key = name:[resource_type]_[resource_name]_[expire_type],etc: "0_ncxxx_1"
        ##value = map<id, counter>
        self.expire = {}

    def start(self, resource_name):
        with self.lock:
            found_name = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_found)
            self.expire[ found_name ] = {}
            lost_name = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_lost)
            self.expire[ lost_name ] = {}
            return True            

    def updateFound(self, resource_name, id_list):
        with self.lock:
            expire_key = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_found)
            if not self.expire.has_key(expire_key):
                return False
            remove_list = []
            for object_id in self.expire[expire_key].keys():
                if object_id not in id_list:
                    remove_list.append(object_id)
            if 0 != len(remove_list):
                for object_id in remove_list:
                    del self.expire[expire_key][object_id]
            for object_id in id_list:
                if self.expire[expire_key].has_key(object_id):
                    ##increase counter
                    self.expire[expire_key][object_id] += 1
                else:
                    ##new counter
                    self.expire[expire_key][object_id] = 1

    def updateLost(self, resource_name, id_list):
        with self.lock:
            expire_key = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_lost)
            if not self.expire.has_key(expire_key):
                return False
            remove_list = []
            for object_id in self.expire[expire_key].keys():
                if object_id not in id_list:
                    remove_list.append(object_id)
            if 0 != len(remove_list):
                for object_id in remove_list:
                    del self.expire[expire_key][object_id]
            for object_id in id_list:
                if self.expire[expire_key].has_key(object_id):
                    ##increase counter
                    self.expire[expire_key][object_id] += 1
                else:
                    ##new counter
                    self.expire[expire_key][object_id] = 1
                    
    def isFound(self, resource_name, object_id, max_expire):
        with self.lock:
            expire_key = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_found)
            if not self.expire.has_key(expire_key):
                return False
            ##increase
            if not self.expire[expire_key].has_key(object_id):
                return False
            ##check
            self.expire[expire_key][object_id] += 1
            if self.expire[expire_key][object_id] < max_expire:
                ##not expire
                return False
            ##expired&clear
            del self.expire[expire_key][object_id]
            return True

    def isLost(self, resource_name, object_id, max_expire):
        with self.lock:
            expire_key = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_lost)
            if not self.expire.has_key(expire_key):
                return False
            ##increase
            if not self.expire[expire_key].has_key(object_id):
                return False
            ##check
            self.expire[expire_key][object_id] += 1
            if self.expire[expire_key][object_id] < max_expire:
                ##not expire
                return False
            ##expired&clear
            del self.expire[expire_key][object_id]
            return True

    def finish(self, resource_name):
        with self.lock:
            found_name = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_found)
            if self.expire.has_key(found_name):
                del self.expire[found_name]
            lost_name = "%d_%s_%d"%(ExpireManager.resource_type_host, resource_name, ExpireManager.expire_type_lost)
            if self.expire.has_key(lost_name):
                del self.expire[lost_name]
            return True            
    
        

#!/usr/bin/python

from storage_pool import StoragePool
import threading
from storage_resource import StorageResource
import logging
from device import Device


class StoragePoolManager(object):
    
    
    def __init__(self):
        self.logger = logging.getLogger("StoragePoolManager")
        
        # {
        # storage_pool_uuid : StoragePool instance,
        # ...
        # }
        self._storage_pool_info = {}
        self._storage_pool_info_lock = threading.RLock()
        
        # {
        # resource_name : StorageResource instance,
        # ...
        # }
        self._storage_resource_info = {}
        self._storage_resource_info_lock = threading.RLock()
        
        # {
        # device_uuid : Device instance,
        # ...
        # }
        self._device_info = {}
        self._device_info_lock = threading.RLock()

    #----------------

    def addStoragePool(self, data_index, storage_pool):
        
        if not isinstance(data_index, str):
            raise Exception("data_index must be str.")
        if not data_index:
            raise Exception("data_index cannot be blank.")
        
        if not isinstance(storage_pool, StoragePool):
            raise Exception("storage_pool must be instance of StoragePool.")
        if not storage_pool:
            raise Exception("storage_pool cannot be None.")
        if not storage_pool.uuid:
            raise Exception("storage_pool.uuid cannot be blank.")
        
        storage_pool.data_index = data_index
        with self._storage_pool_info_lock:
            self._storage_pool_info[storage_pool.uuid] = storage_pool
            
                
    def isStoragePoolUUIDExists(self, storage_pool_uuid):
        with self._storage_pool_info_lock:
            return self._storage_pool_info.has_key(storage_pool_uuid)
                
                
    def getStoragePool(self, storage_pool_uuid):
        
        if not isinstance(storage_pool_uuid, str):
            raise Exception("storage_pool_uuid must be str.")
        if not storage_pool_uuid:
            raise Exception("storage_pool_uuid cannot be blank.")
        
        with self._storage_pool_info_lock:
            if self._storage_pool_info.has_key(storage_pool_uuid):
                return self._storage_pool_info[storage_pool_uuid]
            else:
                return None
                
     
    def removeStoragePool(self, storage_pool_uuid):
        
        if not isinstance(storage_pool_uuid, str):
            raise Exception("storage_pool_uuid must be str.")
        if not storage_pool_uuid:
            raise Exception("storage_pool_uuid cannot be blank.")
        
        with self._storage_pool_info_lock:
            if self._storage_pool_info.has_key(storage_pool_uuid):
                del self._storage_pool_info[storage_pool_uuid]
                return True
            else:
                return False
        
    #------------------
    
    def addStorageResource(self, storage_pool_uuid, storage_resource):

        if not isinstance(storage_pool_uuid, str):
            raise Exception("storage_pool_uuid must be str.")
        if not storage_pool_uuid:
            raise Exception("storage_pool_uuid cannot be blank.")
        
        
        if not isinstance(storage_resource, StorageResource):
            raise Exception("storage_resource must be instance of StorageResource.")
        if not storage_resource:
            raise Exception("storage_resource cannot be None.")
        if not storage_resource.name:
            raise Exception("storage_resource.name cannot be blank.")
        
        
        with self._storage_pool_info_lock:
            
            # LOCK: self._storage_pool_info_lock
            if not self.isStoragePoolUUIDExists(storage_pool_uuid):
                raise Exception("storage_pool_uuid '%s' not exists." % storage_pool_uuid)
            
            storage_resource.storage_pool = storage_pool_uuid
            with self._storage_resource_info_lock:
                self._storage_resource_info[storage_resource.name] = storage_resource
            
            
    def getStorageResource(self, storage_resource_name):
        with self._storage_resource_info_lock:
            if self._storage_resource_info.has_key(storage_resource_name):
                return self._storage_resource_info[storage_resource_name]
            else:
                return None


    def removeStorageResource(self, storage_resource_name):
        with self._storage_resource_info_lock:
            if self._storage_resource_info.has_key(storage_resource_name):
                del self._storage_resource_info[storage_resource_name]
                return True
            else:
                return False

    #---------------------


    def addDevice(self, storage_pool_uuid, device):

        if not isinstance(storage_pool_uuid, str):
            raise Exception("storage_pool_uuid must be str.")
        if not storage_pool_uuid:
            raise Exception("storage_pool_uuid cannot be blank.")
        
        if not isinstance(device, Device):
            raise Exception("device must be instance of Device.")
        if not device:
            raise Exception("device cannot be None.")
        if not device.uuid:
            raise Exception("device.uuid cannot be blank.")
        
        with self._storage_pool_info_lock:
            
            # LOCK: self._storage_pool_info_lock
            if not self.isStoragePoolUUIDExists(storage_pool_uuid):
                raise Exception("storage_pool_uuid '%s' not exists." % storage_pool_uuid)
            
            device.storage_pool = storage_pool_uuid
            with self._device_info_lock:
                self._device_info[device.uuid] = device
            
            
    def getDevice(self, device_uuid):
        with self._device_info_lock:
            if self._device_info.has_key(device_uuid):
                return self._device_info[device_uuid]
            else:
                return None
            

    def deleteDevice(self, device_uuid):
        with self._device_info_lock:
            if self._device_info.has_key(device_uuid):
                del self._device_info[device_uuid]
                return True
            else:
                return False
            
    #---------------------


    def statisticStatus(self):
        return [0, 0, 0, 0]


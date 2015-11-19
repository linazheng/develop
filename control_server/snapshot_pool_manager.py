#!/usr/bin/python
from string import strip
import copy
import threading

class SnapshotPoolManager():

    def __init__(self):
        self.snapshot_pool_info = {}
        self.snapshot_pool_info_lock = threading.RLock()

    # snapshot pool---------------

    def addSnapshotPool(self, snapshot_pool):
        with self.snapshot_pool_info_lock:
            self.snapshot_pool_info[snapshot_pool.uuid] = snapshot_pool

    def getSnapshotPoolDuplication(self, uuid):
        with self.snapshot_pool_info_lock:
            snapshot_pool = self.getSnapshotPool(uuid)
            if snapshot_pool != None:
                return copy.deepcopy(snapshot_pool)

            return None

    def getSnapshotPool(self, uuid):
        with self.snapshot_pool_info_lock:
            if self.snapshot_pool_info.has_key(uuid):
                snapshot_pool = self.snapshot_pool_info[uuid]
                return snapshot_pool

            return None

    def modifySnapshotPool(self, uuid, name):
        with self.snapshot_pool_info_lock:
            snapshot_pool = self.getSnapshotPool(uuid)
            if snapshot_pool != None:
                snapshot_pool.name = name

    def removeSnapshotPool(self, uuid):
        with self.snapshot_pool_info_lock:
            if self.snapshot_pool_info.has_key(uuid):
                del self.snapshot_pool_info[uuid]

    # snapshot node---------------
    def addSnapshotNodeList(self, pool, snapshot_node_list):
        with self.snapshot_pool_info_lock:
            snapshot_pool = self.getSnapshotPool(pool)
            if snapshot_pool != None:
                snapshot_node_map = {}
                for i in xrange(len(snapshot_node_list)):
                    snapshot_node = snapshot_node_list[i]

                    if snapshot_node != None:
                        key = snapshot_node.name
                        snapshot_node_map[key] = snapshot_node

                snapshot_pool.snapshot_node_list = snapshot_node_map

    def addSnapshotNode(self, pool, snapshot_node):
        if snapshot_node != None:
            with self.snapshot_pool_info_lock:
                snapshot_pool = self.getSnapshotPool(pool)
                if snapshot_pool != None:
                    key = snapshot_node.name
                    snapshot_pool.snapshot_node_list[key] = snapshot_node

    def removeSnaspshotNode(self, pool, name):
        if len(strip(name)) != 0:
            with self.snapshot_pool_info_lock:
                snapshot_pool = self.getSnapshotPool(pool)
                if snapshot_pool != None:
                    key = name

                    snapshot_node_list = snapshot_pool.snapshot_node_list
                    if snapshot_node_list.has_key(key):
                        del snapshot_node_list[key]



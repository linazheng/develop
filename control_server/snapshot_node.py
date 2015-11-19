#!/usr/bin/python

class SnapshotNode():
    
    def __init__(self):
        self.name = ""
        self.status = 0
        self.cpu_count = 0
        self.cpu_usage = 0.0
        self.memory = [0, 0]
        self.memory_usage = 0.0
        self.disk_volume = [0, 0]
        self.disk_usage = 0.0
        self.ip = ""
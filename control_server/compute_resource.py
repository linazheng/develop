#!/usr/bin/python

class ComputeResource(object):
    def __init__(self):
        ##service name
        self.name = ""
        self.status = 0
        ##server uuid
        self.server = ""
        ##allocated host id
        self.allocated = set()

    def containsHost(self, uuid):
        return (uuid in self.allocated)

    def removeHost(self, host_id):
        if host_id in self.allocated:
            self.allocated.remove(host_id)

    def addHost(self, host_id):
        if host_id not in self.allocated:
            self.allocated.add(host_id)

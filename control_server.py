#!/usr/bin/env python

from main import Proxy
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from service.message_define import getRequest
import logging
import sys
import threading


class TestServiceProxy(Proxy):

    def attachLogger(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s"))
        handler.setLevel(logging.DEBUG)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
        
    def redirectOutput(self):
        pass
    
    def createService(self):
        service = Proxy.createService(self)
        ##logger
        service.logger.setLevel(logging.DEBUG)
        service.transport.logger.setLevel(logging.DEBUG)
        service.timer.logger.setLevel(logging.DEBUG)
        service.domain_service.logger.setLevel(logging.DEBUG)
        
        return service
    
if __name__ == "__main__":
    proxy = TestServiceProxy();
    if proxy.start() == False:
        print >> sys.stderr, "fail to start."
        sys.exit()
    else:
        print >> sys.stderr, "success to start."
        threading.Event().wait(3)
        
        service = proxy.service
        
        
#         request = getRequest(RequestDefine.flush_disk_image)
#         request.setString(ParamKeyDefine.uuid, "e99bfaec-4d95-4713-bd6f-42a7ca6d2111")
#         request.setUInt(ParamKeyDefine.disk, 0)
#         request.setUInt(ParamKeyDefine.mode, 0)
#         request.setString(ParamKeyDefine.image, "b0e6c9a44c3544abacdb0c48a5cbd882")
#         request.sender = "http_gateway_dev"
#           
#         service.sendMessageToSelf(request)

       
#         request = getRequest(RequestDefine.backup_host)
#         request.setString(ParamKeyDefine.uuid, "64c2c4a2-c513-4094-ac0f-a3571b406422")
#         request.setUInt(ParamKeyDefine.mode, 1)
#         request.setUInt(ParamKeyDefine.disk, 0)
# #         request.sender = "http_gateway_dev"
#             
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.resume_host)
#         request.setString(ParamKeyDefine.uuid, "64c2c4a2-c513-4094-ac0f-a3571b406422")
#         request.setUInt(ParamKeyDefine.mode, 1)
#         request.setUInt(ParamKeyDefine.disk, 0)
# #         request.sender = "http_gateway_dev"
#               
#         service.sendMessageToSelf(request)

#         request = getRequest(RequestDefine.query_host_backup)
#         request.setString(ParamKeyDefine.uuid, "64c2c4a2-c513-4094-ac0f-a3571b406422")
#              
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.add_rule)
#         request.setString(ParamKeyDefine.target, "intelligent_router_dev")
#         request.setUInt(ParamKeyDefine.mode, 0)
#         request.setStringArray(ParamKeyDefine.ip, ["", ""])
#         request.setUIntArray(ParamKeyDefine.port, [80, 0])
#               
#         service.sendMessageToSelf(request)
        
#         request = getRequest(RequestDefine.remove_rule)
#         request.setString(ParamKeyDefine.target, "")
#         request.setUInt(ParamKeyDefine.mode, 0)
#         request.setStringArray(ParamKeyDefine.ip, ["", ""])
#         request.setUIntArray(ParamKeyDefine.port, [80, 0])
#               
#         service.sendMessageToSelf(request)

#         request = getRequest(RequestDefine.query_rule)
#         request.setString(ParamKeyDefine.target, "intelligent_router_dev")
#               
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.modify_compute_pool)
#         request.setString(ParamKeyDefine.uuid, "b5d65729e53c4cac8df008198fea9a97")
#         request.setString(ParamKeyDefine.name, "default")
#         request.setUInt(ParamKeyDefine.network_type, 0)
#         request.setUInt(ParamKeyDefine.disk_type, 0)
#         request.setString(ParamKeyDefine.path, "path_0")
#         request.setString(ParamKeyDefine.crypt, "crypt_0")
#                   
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.query_compute_pool_detail)
#         request.setString(ParamKeyDefine.uuid, "f4986d401bca4f77a2503f80b06fbde0")
#                   
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.reset_host)
#         request.setString(ParamKeyDefine.uuid, "735b6956-fc18-46c3-b87d-c7a6659a69e")
#                 
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.query_storage_device)
#         request.setUInt(ParamKeyDefine.level, 1)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 0)
#                  
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.add_storage_device)
#         request.setUInt(ParamKeyDefine.level, 1)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 0)

#         request = getRequest(RequestDefine.remove_storage_device)
#         request.setUInt(ParamKeyDefine.level, 1)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 0)

#         request = getRequest(RequestDefine.enable_storage_device)
#         request.setUInt(ParamKeyDefine.level, 1)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 0)

#         request = getRequest(RequestDefine.disable_storage_device)
#         request.setUInt(ParamKeyDefine.level, 1)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 0)
#                  
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.create_compute_pool)
#         request.setString(ParamKeyDefine.name, "test")
#         request.setUInt(ParamKeyDefine.network_type, 0)
#         request.setUInt(ParamKeyDefine.disk_type, 2)
#         request.setString(ParamKeyDefine.path, "path0")
#         request.setString(ParamKeyDefine.crypt, "crypt0")
#         
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.modify_service)
#         request.setUInt(ParamKeyDefine.type, 3)
#         request.setString(ParamKeyDefine.target, "node_client_000c29d74563")
#         request.setUInt(ParamKeyDefine.disk_type, 2)
#         request.setString(ParamKeyDefine.disk_source, "path_0")
#         request.setString(ParamKeyDefine.crypt, "crypt_0")
#          
#         service.sendMessageToSelf(request)

#         request = getRequest(RequestDefine.query_service)
#         request.setUInt(ParamKeyDefine.type, 3)
#         request.setString(ParamKeyDefine.group, "default")
#           
#         service.sendMessageToSelf(request)


#         request = getRequest(RequestDefine.insert_media)
#         request.setString(ParamKeyDefine.uuid, "62550e8b-a918-49e2-b5ad-7e78746cc338")
#         request.setString(ParamKeyDefine.image, "b599653042d54b11a8652cda7cbf9947")
#          
#         service.sendMessageToSelf(request)

#         request = getRequest(RequestDefine.change_media)
#         request.setString(ParamKeyDefine.uuid, "62550e8b-a918-49e2-b5ad-7e78746cc338")
#         request.setString(ParamKeyDefine.image, "b599653042d54b11a8652cda7cbf9947")
#          
#         service.sendMessageToSelf(request)
        
#     threading.Event().wait(5)
#     proxy.stop()

#!/usr/bin/python


from transaction.base_task import BaseTask
from service.message_define import RequestDefine, ParamKeyDefine, getResponse

class DeleteNetworkTask(BaseTask):
    
    
    def __init__(self, task_type, messsage_handler, network_manager, address_manager):
        self.network_manager    = network_manager
        self.address_manager    = address_manager
        logger_name = "task.delete_network"
        BaseTask.__init__(self, task_type, RequestDefine.delete_network, messsage_handler, logger_name)

    
    def invokeSession(self, session):
        
        request = session.initial_message
        
        _parameter = {}
        _parameter["uuid"]        = request.getString(ParamKeyDefine.uuid)
        
        self.info("[%08X] <delete_network> receive delete network request from '%s', parameter: %s" % ( session.session_id, 
                                                                                                        session.request_module, 
                                                                                                        _parameter))
        
        # check vpc network
        _networkInfo = self.network_manager.getNetwork(_parameter["uuid"])
        if _networkInfo==None:
            self.error("[%08X] <delete_network> delete network fail, invalid uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        # check attached host(s)
        attached_hosts_count = len(_networkInfo.hosts)
        if attached_hosts_count>0:
            self.error("[%08X] <delete_network> delete network fail, %s host(s) attach to network '%s'" % (session.session_id, attached_hosts_count, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        # delete public ip
        _deallocated_ips = []
        for _public_ip in _networkInfo.public_ips:
            if self.address_manager.deallocate(_networkInfo.pool, _public_ip):
                _deallocated_ips.append(_public_ip)
        self.network_manager.detachAddress(_networkInfo.uuid, _deallocated_ips)
        
#         public_ips_count = len(_networkInfo.public_ips)
#         if public_ips_count>0:
#             self.error("[%08X] <delete_network> delete network fail, %s public ip(s) allocated to network '%s'" % (session.session_id, public_ips_count, _parameter["uuid"]))
#             self.taskFail(session)
#             return
        
        if not self.network_manager.deleteNetwork(_parameter["uuid"]):
            self.error("[%08X] <delete_network> delete network fail, uuid '%s'" % (session.session_id, _parameter["uuid"]))
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.delete_network)
        response.session = session.request_session
        response.success = True
        self.sendMessage(response, session.request_module)
        session.finish()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


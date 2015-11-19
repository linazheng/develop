#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *

class QueryHostInfoTask(BaseTask):
    
    def __init__(self, task_type, messsage_handler, config_manager):
        self.config_manager = config_manager
        logger_name = "task.query_host_info"
        BaseTask.__init__(self, task_type, RequestDefine.query_host_info, messsage_handler, logger_name)

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = session.initial_message
        uuid = request.getString(ParamKeyDefine.uuid)
        
        host = self.config_manager.getHost(uuid)
        if host==None:
            self.error("[%08X] <query_host_info> query host info fail, invalid id '%s'"%(session.session_id, uuid))
            self.taskFail(session)
            return
        
        response = getResponse(RequestDefine.query_host_info)
        response.session = session.request_session
        response.success = True
        response.setString(ParamKeyDefine.name,    host.name)
        response.setUInt(ParamKeyDefine.cpu_count, host.cpu_count)
        response.setUInt(ParamKeyDefine.memory,    host.memory)
        option = []
        
        ##auto start
        if host.auto_start:
            option.append(1)
        else:
            option.append(0)
            
        ##data disk
        option.append(host.data_disk_count)
        option.append(host.enable_local_backup)
        option.append(host.enable_usb_ext)
        option.append(host.video_type)
        response.setUIntArray(ParamKeyDefine.option,      option)
        response.setUIntArray(ParamKeyDefine.disk_volume, host.disk_volume)

        # port
        port = []
        for host_port in host.port:
            port.extend([host_port.protocol,
                         host_port.server_port,
                         host_port.host_port,
                         host_port.public_port])
        
        # ip
        ip = [host.server_ip]
        display_port = [host.server_port]
        
        if host.public_ip:
            ip.append(host.public_ip)
            display_port.append(host.public_port)
        elif host.vpc_ip:
            ip.append(host.vpc_ip)
            display_port.append(host.server_port)
        else:
            ip.append("")
            display_port.append(0)
            
        response.setUIntArray(ParamKeyDefine.port, port)

        response.setString(ParamKeyDefine.user,           host.user)
        response.setString(ParamKeyDefine.group,          host.group)
        response.setString(ParamKeyDefine.display,        host.display)
        response.setString(ParamKeyDefine.authentication, host.authentication)
        response.setString(ParamKeyDefine.network,        host.network)

        response.setUInt(ParamKeyDefine.inbound_bandwidth,  host.inbound_bandwidth)
        response.setUInt(ParamKeyDefine.outbound_bandwidth, host.outbound_bandwidth)
        response.setUInt(ParamKeyDefine.io, host.max_iops)
        response.setUInt(ParamKeyDefine.priority, host.cpu_priority)
        
        response.setStringArray(ParamKeyDefine.ip,         ip)
        response.setUIntArray(ParamKeyDefine.display_port, display_port)

        response.setString(ParamKeyDefine.forward,         host.forwarder)
        response.setUInt(ParamKeyDefine.network_type,      host.network_type)
        response.setString(ParamKeyDefine.network_source,  host.network_source)
        response.setUInt(ParamKeyDefine.disk_type,         host.disk_type)
        response.setString(ParamKeyDefine.disk_source,     host.disk_source)
        
        self.info("[%08X] <query_host_info> query host info success, host name '%s'"%(session.session_id, host.name))
        
        self.sendMessage(response, session.request_module)
        session.finish()

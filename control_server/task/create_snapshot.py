#!/usr/bin/python
from service.message_define import EventDefine
from service.message_define import ParamKeyDefine
from service.message_define import RequestDefine
from transaction.base_task import BaseTask
from transaction.state_define import result_any
from transaction.state_define import result_fail
from transaction.state_define import result_success
from transaction.state_define import state_finish
from transaction.state_define import state_initial
from transport.app_message import AppMessage
from common import dict_util


class CreateSnapshotTask(BaseTask):


    timeout = 5


    def __init__(self, task_type, message_handler, config_manager):
        self.config_manager = config_manager
        logger_name = "task.create_snapshot"
        BaseTask.__init__(self, task_type, RequestDefine.create_snapshot, message_handler, logger_name)

        # state inital
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_snapshot, result_success, self.onSuccess, state_finish );
        self.addTransferRule(state_initial, AppMessage.RESPONSE, RequestDefine.create_snapshot, result_fail,    self.onFail,    state_finish );
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.report,            result_any,     self.onReport );
        self.addTransferRule(state_initial, AppMessage.EVENT,    EventDefine.timeout,           result_any,     self.onTimeout, state_finish );


    def invokeSession(self, session):
        request = session.initial_message
        
        v_type    = request.getUInt(ParamKeyDefine.type)
        v_target  = request.getString(ParamKeyDefine.target)
        v_mode    = request.getUInt(ParamKeyDefine.mode)
        v_index   = request.getUInt(ParamKeyDefine.index)
        
        v_parameter = {}
        v_parameter["type"]   =  v_type;
        v_parameter["target"] =  v_target;
        v_parameter["mode"]   =  v_mode;
        v_parameter["index"]  =  v_index;
        
        session_ext_data = {}
        session_ext_data["parameter"] = v_parameter;
        
        self.info("[%08X] <create_snapshot> receive create snapshot request from '%s', parameter: %s" % (session.session_id, session.request_module, dict_util.toDictionary(v_parameter)))
        
        # instance of HostInfo
        host = self.config_manager.getHost(v_target)
        if host is None:
            self.error("[%08X] <create_snapshot> create snapshot fail, invalid id '%s'" % (session.session_id, v_target))
            self.taskFail(session)
            return
        
        # 
        self.info("[%08X] <create_snapshot> send create_snapshot request to node_client '%s'" % (session.session_id, host.container))
        
        # 
        if not self.message_handler.sendMessage(request, host.container):
            self.taskFail(session)
            return

        self.setTimer(session, self.timeout)
        
        
        
    def onSuccess(self, response, session):
        self.clearTimer(session)
        v_resp_uuid = response.getString(ParamKeyDefine.uuid);
        self.info("[%08X] <create_snapshot> create snapshot for host '%s' success, newly created snapshot uuid is '%s'" % (session.session_id, 
                                                                                                                           session._ext_data["parameter"]["target"], 
                                                                                                                           v_resp_uuid))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()
        
        
    def onReport(self, response, session):
        request = session.initial_message
        v_level = request.getUInt(ParamKeyDefine.level)
        self.info("[%08X] <create_snapshot> report creating snapshot for host '%s' at level '%s'." % (session.session_id, session._ext_data["parameter"]["target"], v_level))


    def onFail(self, response, session):
        self.clearTimer(session)
        self.info("[%08X] <create_snapshot> create snapshot for host '%s' fail." % (session.session_id, session._ext_data["parameter"]["target"]))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()


    def onTimeout(self, response, session):
        self.clearTimer(session)
        self.info("[%08X] <create_snapshot> create snapshot for host '%s' timeout." % (session.session_id, session._ext_data["parameter"]["target"]))
        response.session = session.request_session
        self.sendMessage(response, session.request_module)
        session.finish()



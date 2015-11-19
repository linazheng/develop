#!/usr/bin/python
# -*- coding: utf-8 -*-
from transaction.base_session import *

class TaskSession(BaseSession):
    def reset(self):
        """
        reset session params,should override
        """
        BaseSession.reset(self)
        self.data_server = ""
        self.statistic_server = ""
        ##new added for 2.0
        self.target_list = []
        self.offset = 0
        self.total = 0
        self.target = ""
        self.remote_session = 0
        self.counter = 0

        


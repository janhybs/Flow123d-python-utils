#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from scripts.prescriptions import AbstractRun


class PBSModule(AbstractRun):
    def __init__(self, case):
        super(PBSModule, self).__init__(case)
        self.queue = 'default'
        self.ppn = 1

    def get_pbs_command(self, pbs_script_filename):
        """
        :rtype: list[str]
        """
        pass

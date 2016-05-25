#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import subprocess

import time
import subprocess
import csv

from utils.dotdict import Map


class Execute(subprocess.Popen):
    platform = 'cygwin'
    MEMORY_TUPLE = ('node', 'vms', 'rss')

    def __init__(self, *args, **kwargs):
        super(Execute, self).__init__(*args, **kwargs)
        self.refresh_period = 5
        self._last_refresh = 0
        self._memory_info = dict()

        self._refresh()

    @property
    def last_refresh(self):
        return time.time() - self._last_refresh

    def _refresh(self):
        if self.last_refresh < self.refresh_period:
            return
        self._last_refresh = time.time()

        command = 'wmic process where ProcessId="{}" get VirtualSize,WorkingSetSize /format:csv'
        # memory_info = subprocess.check_output([command.format(self.pid)], shell=True)
        memory_info = '\r\r\nNode,VirtualSize,WorkingSetSize\r\r\nFoo,1564654,164564\r\r\n'
        memory_info = memory_info.strip()

        info = [x for x in csv.reader(memory_info.splitlines()) if x]
        if len(info) != 2:
            # refresh failed
            return

        # zip with tuple (node
        self._memory_info = Map(dict(zip(self.MEMORY_TUPLE, info[1])))

    def memory_info(self):
        self._refresh()
        return self._memory_info


e = Execute(['sleep', '1'])
print e.memory_info().rss
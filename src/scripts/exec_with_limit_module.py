#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from __future__ import absolute_import

from scripts.execs.monitor import LimitMonitor, ProcessMonitor
from scripts.execs.test_executor import BinExecutor
from utils.argparser import ArgParser

usage = "exec_with_limit.py [-t <time>] [-m <memory>] -- <executable> <arguments>"

parser = ArgParser(usage)
parser.add('-t', '--limit-time', type=float, name='time_limit', placeholder='<time>', docs=[
    'Obligatory wall clock time limit for execution in seconds',
    'For precision use float value'
])
parser.add('-m', '--limit-memory', type=float, name='memory_limit', placeholder='<memory>', docs=[
    'Optional memory limit per node in MB',
    'For precision use float value'
])


def do_work():
    # parse arguments
    options, others, rest = parser.parse()

    # prepare executor
    executor = BinExecutor(rest)
    process_monitor = ProcessMonitor(executor)

    # set limits
    limiter = LimitMonitor(process_monitor)
    limiter.time_limit = options.time_limit
    limiter.memory_limit = options.memory_limit
    process_monitor.add_monitor(limiter)

    # start process
    process_monitor.start()

do_work()
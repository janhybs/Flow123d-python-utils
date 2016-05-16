#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from __future__ import absolute_import
from scripts.core.base import Printer

from scripts.execs.monitor import LimitMonitor, ProcessMonitor
from scripts.execs.test_executor import BinExecutor


def do_work(frontend_file, parser):
    """
    :type frontend_file: str
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    options, others, rest = parser.parse()

    # check commands
    if not rest:
        parser.exit_usage('No command specified!')

    # check limits (at least one limit must be set)
    if (options.time_limit, options.memory_limit) == (None, None):
        parser.exit_usage('No limits specified!')

    # prepare executor
    executor = BinExecutor(rest)
    process_monitor = ProcessMonitor(executor)

    # set limits
    process_monitor.limit_monitor.time_limit = options.time_limit
    process_monitor.limit_monitor.memory_limit = options.memory_limit

    # start process
    Printer.out('-' * 60)
    process_monitor.start()
#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from __future__ import absolute_import
import pathfix
# ----------------------------------------------
from utils.argparser import ArgParser


parser = ArgParser("exec_with_limit.py [-t <time>] [-m <memory>] -- <executable> <arguments>")
# ----------------------------------------------
parser.add('-t', '--limit-time', type=float, name='time_limit', placeholder='<time>', docs=[
    'Obligatory wall clock time limit for execution in seconds',
    'For precision use float value'
])
parser.add('-m', '--limit-memory', type=float, name='memory_limit', placeholder='<memory>', docs=[
    'Optional memory limit per node in MB',
    'For precision use float value'
])
parser.add_section('Proposed arguments')
parser.add('', '--root', type=str, name='root', placeholder='<root>', docs=[
    'Optional hint for flow123d path, if not specified, default value will be',
    'Extracted from this file path, assuming it is located in flow123d bin/python dir',
    '',
    'Script will always change-dir itself to location of root, so all path match'
])
# ----------------------------------------------

if __name__ == '__main__':
    from scripts.exec_with_limit_module import do_work
    do_work(__file__, parser)

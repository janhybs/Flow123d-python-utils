#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
# if env variable FLOWLOC is set, copy python files in correct folders
# for example /et/profile: export FLOWLOC=/home/jan-hybs/projects/Flow123d/flow123d

import os, sys
from shutil import copyfile

src_dir = os.path.join(os.path.dirname(__file__), 'src')
flow_dir = os.environ['FLOWLOC']

bin_python = os.path.join(flow_dir, 'bin', 'python')
src_python = os.path.join(flow_dir, 'src', 'python')


def rel(target):
    return os.path.relpath(target, src_dir)


def cp2src(target):
    if os.path.isfile(target) and target.endswith('.py'):
        tt = os.path.join(src_python, rel(target))
        copyfile(target, tt)
        print 'COPY  src/python file', os.path.relpath(tt, flow_dir)

    if os.path.isdir(target):
        path = os.path.join(src_python, rel(target))
        if not os.path.exists(path):
            print 'MKDIR src/python file', os.path.relpath(path, flow_dir)
            os.mkdir(path)

        for t in [os.path.join(target, x) for x in os.listdir(target)]:
            cp2src(t)


if flow_dir:
    targets = [os.path.join(src_dir, x) for x in os.listdir(src_dir)]
    for t in targets:

        # files on 1 level to bin/python
        if os.path.isfile(t):
            if t.endswith('.py') or t.endswith("requirements.txt"):
                tt = os.path.join(bin_python, rel(t))
                copyfile(t, tt)
                print 'COPY  bin/python file', os.path.relpath(tt, flow_dir)

        # files and folders on other level to src/python
        if os.path.isdir(t):
            cp2src(t)
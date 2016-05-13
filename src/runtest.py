#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from __future__ import absolute_import
import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    from scripts.runtest_module import do_work
    do_work(__file__)
#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
# ----------------------------------------------
import os
import shutil
import sys
import time
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
# ----------------------------------------------
import test_scripts
test_scripts.fix_paths()
# ----------------------------------------------
from runtest import parser
from scripts.runtest_module import do_work
# ----------------------------------------------
__dir__ = test_scripts.current_dir()
extras = os.path.join(__dir__, 'extras')

root = r'/home/jan-hybs/Dokumenty/projects/Flow123d/flow123d'
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_COMPARE_ERROR = 13


class TestDoWork(test_scripts.UnitTest):
    """
    Class TestDoWork tests interface for script runtest.py and backend runtest_module
    """

    @test_scripts.limit_test(hostname='*')
    def test_single_pbs(self):
        pass
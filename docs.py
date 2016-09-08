#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import os
from subprocess import check_output

__dir__ = os.path.dirname(os.path.realpath(__file__))


src = os.path.join(__dir__, 'src')
test = os.path.join(__dir__, 'test')

print check_output(['find', src])
#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import psutil


class Execute(psutil.Popen):
    platform = 'windows'

    def __init__(self, *args, **kwargs):
        super(Execute, self).__init__(*args, **kwargs)

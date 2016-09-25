#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import yaml
import os
import shutil
import formic


class CopyRule(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __repr__(self):
        return 'CopyRule({self.source} => {self.target})'.format(self=self)

    def copy(self):
        if not os.path.exists(os.path.dirname(self.target)):
            os.makedirs(os.path.dirname(self.target))

        shutil.copy(self.source, self.target)


class YAMLTag(yaml.YAMLObject):
    def __setstate__(self, state):
        """ :type state: dict """
        self.__init__(**state)


class Collector(YAMLTag):
    yaml_tag = u'!Collector'

    def __init__(self, source=None, target=None, includes='*', excludes=None, flat=False, **kwargs):
        self.source = source
        self.target = target
        self.includes = includes
        self.excludes = excludes
        self.flat = flat
        self.__dict__.update(kwargs)

    def __iter__(self):
        fileset = formic.FileSet(self.includes, directory=self.source)
        for filename in fileset:
            if self.flat:
                yield CopyRule(filename, os.path.join(self.target, os.path.basename(filename)))
            else:
                target_dest = os.path.relpath(filename, os.path.abspath(self.source))
                target_dest = os.path.abspath(os.path.join(self.target, target_dest))
                yield CopyRule(filename, target_dest)

    def __repr__(self):
        return 'Collector({self.source} => {self.target})'.format(self=self)


with open('artifact.yml', 'r') as fp:
    configuration = yaml.load(fp)
    for col in configuration['collectors']:
        for rule in col:
            print rule.copy()

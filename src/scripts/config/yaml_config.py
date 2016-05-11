#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import yaml
import copy
import itertools

from scripts.core.base import Paths
from scripts.execs.test_executor import TestPrescription, MPIPrescription
from utils.globals import ensure_iterable


default_values = dict(
    proc=[1],
    time_limit=30,
    memory_limit=400,
    check_rules=[]
)


class YamlConfigCase(object):
    def __init__(self,  config, o={}):
        """
        :type config: YamlConfig
        """
        self.proc = self._get(o, 'proc')
        self.time_limit = self._get(o, 'time_limit')
        self.memory_limit = self._get(o, 'memory_limit')
        self.check_rules = self._get(o, 'check_rules')
        self.files = ensure_iterable(self._get(o, 'file'))
        self.config = config
        for i in range(len(self.files)):
            self.files[i] = Paths.join(config.root, self.files[i])

    @classmethod
    def _get(cls, o, prop):
        return o.get(prop, default_values.get(prop))

    def __repr__(self):
        return '<TestCase {self.files}>'.format(self=self)


class YamlConfig(object):
    """
    :type test_cases: list[YamlConfigCase]
    :type common_config: dict
    """
    def __init__(self, filename):
        # prepare paths
        self.filename = filename
        self.root = Paths.dirname(self.filename)
        self.test_results = Paths.join(self.root, 'test_results')
        self.ref_output = Paths.join(self.root, 'ref_output')
        self.input = Paths.join(self.root, 'input')

        # list yaml files which are not 'config.yaml' files
        # self.yaml_files = Paths.browse(self.root, [
        #     PathFilters.filter_type_is_file(),
        #     PathFilters.filter_ext('.yaml'),
        #     PathFilters.filter_not(PathFilters.filter_name('config.yaml'))
        # ])

        # read config
        with open(self.filename, 'r') as fp:
            self._yaml = yaml.load(fp)

        # update common config using global values
        self.common_config = self._get(('common_config', 'commons'), {})
        self.common_config = self.merge(default_values, self.common_config)

        # update test_cases using common config values
        self.test_cases = list()
        test_cases = self._get('test_cases', [])
        for test_case in test_cases:
            test_case = self.merge(self.common_config, test_case)
            self.test_cases.append(YamlConfigCase(self, test_case))
        self._iter_index = 0

    def get(self, index):
        """
        :rtype : YamlConfigCase
        """
        return self.test_cases[index]

    def _get(self, names, default=None):
        if type(names) in (list, tuple):
            for name in names:
                result = self._yaml.get(name, None)
                if result:
                    return result
            return default
        else:
            return self._yaml.get(names, default)

    def get_all_cases(self):
        """
        :rtype : list[TestPrescription]
        """
        tmp_result = list()
        # prepare product of all possible combinations of input arguments
        # for now we use only proc (cpu list) and files (file)
        for test_case in self.test_cases:
            tmp_result.append(list(itertools.product(
                ensure_iterable(test_case),
                ensure_iterable(test_case.proc),
                ensure_iterable(test_case.files),
            )))
        result = list()
        for lst in tmp_result:
            # result.extend([TestPrescription(*x) for x in lst])
            result.extend([MPIPrescription(*x) for x in lst])
        return result

    @classmethod
    def merge(cls, parent, children):
        """
        :type parent: dict
        """
        parent_copy = copy.deepcopy(parent)
        children = ensure_iterable(children)
        for child in children:
            parent_copy.update(child)
        return parent_copy

    def __iter__(self):
        self.iter_index = 0
        return self

    def next(self):
        """
        :rtype : YamlConfigCase
        """
        if self._iter_index >= len(self.test_cases):
            raise StopIteration
        else:
            self._iter_index += 1
            return self.test_cases[self._iter_index - 1]

    __next__ = next
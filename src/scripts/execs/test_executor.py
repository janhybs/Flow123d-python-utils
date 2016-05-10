#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from scripts.base import Paths


class TestExecutor(object):
    def __init__(self, test_case, proc_value, filename):
        """
        :type filename: str
        :type proc_value: int
        :type test_case: scripts.config.yaml_config.YamlConfigCase
        """
        self.test_case = test_case
        self.proc_value = proc_value
        self.filename = filename
        # self._filename = Paths.basename(self.filename)
        self.output_name = '_{}.{}'.format(
            Paths.basename(Paths.without_ext(self.filename)),
            self.proc_value
        )
        self.output_dir = Paths.join(test_case.config.test_results, self.output_name)

    def get_command(self):
        return [
            Paths.flow123d(),
            '-s', self.filename,
            '-i', self.test_case.config.input,
            '-o', self.output_dir
        ]

    def __repr__(self):
        return '<Exec {self.output_name}>'.format(self=self)
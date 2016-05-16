#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import shutil
import math
from scripts.core.base import Paths, Printer, PathFilters
from scripts.execs.monitor import ProcessMonitor
from scripts.execs.test_executor import BinExecutor, SequentialProcesses, ExtendedThread


class TestPrescription(object):
    def __init__(self, test_case, proc_value, filename):
        """
        :type filename: str
        :type proc_value: int
        :type test_case: scripts.config.yaml_config.YamlConfigCase
        """
        self.test_case = test_case
        self.proc_value = proc_value
        self.filename = filename

        if not self.filename:
            return

        self.shortname = Paths.basename(Paths.without_ext(self.filename))
        self.ref_output = Paths.join(
            test_case.config.ref_output,
            self.shortname
        )
        self.output_name = '_{}.{}'.format(
            self.shortname,
            self.proc_value
        )
        self.output_dir = Paths.join(test_case.config.test_results, self.output_name)
        self.ndiff_log = Paths.join(self.output_dir, 'ndiff.log')
        self.pbs_script = Paths.join(self.output_dir, 'pbs_script.qsub')

    def _get_command(self):
        return [
            Paths.flow123d(),
            '-s', self.filename,
            '-i', self.test_case.config.input,
            '-o', self.output_dir
        ]

    def get_command(self):
        return [str(x) for x in self._get_command()]

    def __repr__(self):
        return '<{self.__class__.__name__} {self.output_name}>'.format(self=self)

    def _get_mirror_files(self, paths):
        return [
            Paths.join(self.output_dir, Paths.relpath(p, self.ref_output))
            for p in paths
        ]

    def get_ref_output_ndiff_files(self):
        ndiff = self.test_case.check_rules.get('ndiff', {})
        # no filters for ndiff? return empty list so save some IO ops
        if not ndiff:
            return list()

        filters = [PathFilters.filter_wildcards(x) for x in ndiff.get('filters', [])]
        paths = Paths.walk(self.ref_output, [PathFilters.filter_type_is_file()])
        paths = Paths.match(paths, filters)

        return zip(paths, self._get_mirror_files(paths))

    def create_clean_thread(self):
        def target():
            if Paths.exists(self.output_dir):
                Printer.out('Cleaning output dir {}'.format(self.output_dir))
                shutil.rmtree(self.output_dir)
        return ExtendedThread(target=target)

    def create_comparison_threads(self):
        pairs = self.get_ref_output_ndiff_files()
        compares = SequentialProcesses()
        compares.thread_name_property = True
        compares.name = "File compare"
        for pair in pairs:
            pm = ProcessMonitor(
                BinExecutor([
                    Paths.ndiff(),
                    Paths.abspath(pair[0]),
                    Paths.abspath(pair[1])
                ]))
            pm.name = '{} {}'.format(Paths.basename(pair[0]), Paths.filesize(pair[0], True))
            pm.info_monitor.stdout_stderr = self.ndiff_log
            compares.add(pm)
        return compares


class MPIPrescription(TestPrescription):
    def __init__(self, test_case, proc_value, filename):
        super(MPIPrescription, self).__init__(test_case, proc_value, filename)

    def _get_command(self):
        return [
            Paths.mpiexec(),
            '-np', self.proc_value
        ] + super(MPIPrescription, self)._get_command()


class PBSModule(TestPrescription):
    def _get_command(self):
        return [
            'mpirun',
            '-n', self.proc_value
        ] + super(PBSModule, self)._get_command()

    def get_pbs_command(self, options, pbs_script_filename):
        """
        Method will generate all command which will then create PBS job
        :type options: utils.argparser.ArgOptions
        """
        raise NotImplementedError('Method must be implemented in sub classes')

    @staticmethod
    def format(template, **kwargs):
        t = str(template)
        for k, v in kwargs.items():
            t = t.replace('$${}$$'.format(k), v)
        return t

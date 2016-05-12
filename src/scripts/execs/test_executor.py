#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from __future__ import absolute_import

from subprocess import PIPE
import threading
import time

import psutil, shutil
from progressbar import ProgressBar, Bar, Counter

from scripts.core.base import Paths, PathFilters, Printer
from scripts.execs.monitor import ProcessMonitor
from utils.counter import ProgressCounter
from utils.globals import ensure_iterable


class ExtendedThread(threading.Thread):
    def __init__(self, target=None):
        super(ExtendedThread, self).__init__(target=target)
        self._is_over = False

    def run(self):
        super(ExtendedThread, self).run()
        self._is_over = True

    def is_over(self):
        return self._is_over


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

    def get_command(self):
        return [
            Paths.flow123d(),
            '-s', self.filename,
            '-i', self.test_case.config.input,
            '-o', self.output_dir
        ]

    def __repr__(self):
        return '<Exec {self.output_name}>'.format(self=self)

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

    def get_command(self):
        return [
            Paths.mpiexec(),
            '-np', self.proc_value
        ] + super(MPIPrescription, self).get_command()


class BinExecutor(ExtendedThread):
    """
    :type process: psutil.Popen
    """
    def __init__(self, command=list()):
        self.command = [str(x) for x in ensure_iterable(command)]
        self.process = None
        self.running = False
        self.stdout = PIPE
        self.stderr = PIPE
        self.returncode = None
        super(BinExecutor, self).__init__()

    def run(self):
        # run command and block current thread
        try:
            self.process = psutil.Popen(self.command, stdout=self.stdout, stderr=self.stderr)
            self.process.wait()
            super(BinExecutor, self).run()
        except Exception as e:
            # broken process
            self.process = BrokenProcess(e)
        self.returncode = getattr(self.process, 'returncode', None)


class BrokenProcess(object):
    def __init__(self, exception=None):
        self.exception = exception
        self.pid = -1
        self.returncode = 666

    def is_running(self):
        return False


class ParallelProcesses(ExtendedThread):
    """
    :type threads: list[threading.Thread]
    """
    def __init__(self, *args):
        super(ParallelProcesses, self).__init__()
        self.threads = list()
        self.threads.extend(args)

    def add(self, thread):
        self.threads.append(thread)

    def run(self):
        for t in self.threads:
            t.start()

        for t in self.threads:
            t.join()
        super(ParallelProcesses, self).run()


class SequentialProcesses(ExtendedThread):
    """
    :type threads: list[threading.Thread]
    """
    def __init__(self, pbar=True, *args):
        super(SequentialProcesses, self).__init__()
        self.pbar = pbar
        self.threads = list()
        self.threads.extend(args)
        self.name = ''
        self.thread_name_property = False
        self.stop_on_error = False
        self.returncode = None

    def add(self, thread):
        self.threads.append(thread)

    def run(self):
        total = len(self.threads)
        rcs = [None]
        pc = None

        if self.pbar:
            if self.thread_name_property:
                pc = ProgressCounter('{self.name}: {:02d}/{total:02d} ({t.name})')
            else:
                pc = ProgressCounter('{self.name}: {:02d}/{total:02d}')

        for t in self.threads:
            if self.pbar:
                pc.next(locals())

            t.start()
            t.join()
            rc = getattr(t, 'returncode', None)
            rcs.append(rc)

            if self.stop_on_error and rc > 0:
                Printer.err('Aborted next operations due to error')
                break

        self.returncode = max(rcs)
        super(SequentialProcesses, self).run()


class ParallelRunner(object):
    """
    :type threads: list[scripts.execs.test_executor.ExtendedThread]
    """
    def __init__(self, n=4):
        self.n = n
        self.i = 0
        self.threads = list()

    def add(self, process):
        self.threads.append(process)

    def active_count(self):
        total = 0
        for process in self.threads:
            total += 1 if process.is_alive() else 0
        return total

    def complete_count(self):
        total = 0
        for process in self.threads:
            total += 1 if process.is_over() else 0
        return total

    def run(self):
        self.i = 0
        total = len(self.threads)

        fd = FD()
        pbar = ProgressBar(maxval=total, fd=fd, widgets=[], term_width=24)
        pbar.start()
        while self.i < total:
            while self.active_count() < self.n:
                pbar.update(self.i + 1)
                Printer.out('{} {}'.format(
                    'Case {:02d} of {:02d}'.format(self.i + 1, total),
                    fd.data, '5', '6'
                    )
                )
                self.threads[self.i].start()
                self.i += 1

                # no more processes
                if self.i >= total:
                    break
                # sleep a bit to other threads can be active again
                time.sleep(0.1)
            time.sleep(0.1)
        pbar.finish()


class FD(object):
    def __init__(self):
        self.data = ''

    def write(self, data=''):
        self.data = data[:-1] if data.endswith('\r') else data
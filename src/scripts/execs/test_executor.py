#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from subprocess import PIPE

import threading, psutil, time
import sys
from scripts.base import Paths
from progressbar import ProgressBar, Counter


class ExtendedThread(threading.Thread):
    def __init__(self):
        super(ExtendedThread, self).__init__()
        self._is_over = False

    def run(self):
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


class Executor(ExtendedThread):
    """
    :type process: psutil.Popen
    """

    def __init__(self, command=list()):
        self.command = command
        self.process = None
        self.running = False
        super(Executor, self).__init__()

    def run(self):
        # run command and block current thread
        time.sleep(1)
        self.process = psutil.Popen(self.command, stdout=PIPE, stderr=PIPE)
        self.process.wait()
        super(Executor, self).run()


class MultiProcess(ExtendedThread):
    """
    :type threads: list[threading.Thread]
    """
    def __init__(self, *args):
        super(MultiProcess, self).__init__()
        self.threads = list()
        self.threads.extend(args)

    def add(self, thread):
        self.threads.append(thread)

    def run(self):
        for t in self.threads:
            t.start()

        for t in self.threads:
            t.join()
        super(MultiProcess, self).run()


class ParallelRunner(object):
    """
    :type threads: list[ExtendedThread]
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

        def pb():
            last_count = 0
            while self.complete_count() != total:
                current_count = self.complete_count()
                if last_count != current_count:
                    # print '-' * 60
                    print 'Finished: {}/{}'.format(current_count, total)
                    # print '-' * 60
                    last_count = current_count
                time.sleep(0.01)

        threading.Thread(target=pb).start()

        while self.i < total:
            while self.active_count() < self.n:
                self.threads[self.i].start()
                self.i += 1

                # no more processes
                if self.i >= total:
                    break
                # sleep a bit to other threads can be active again
                time.sleep(0.1)
            time.sleep(0.1)

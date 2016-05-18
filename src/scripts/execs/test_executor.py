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
from scripts.execs.monitor import PyProcess
from utils.counter import ProgressCounter
from utils.globals import ensure_iterable


class ExtendedThread(threading.Thread):
    def __init__(self, name, target=None):
        super(ExtendedThread, self).__init__(name=name, target=target)
        self._is_over = False
        self.name = name
        assert type(name) is str

    def run(self):
        super(ExtendedThread, self).run()
        self._is_over = True

    def is_over(self):
        return self._is_over


class BinExecutor(ExtendedThread):
    """
    :type process: psutil.Popen
    """
    def __init__(self, command=list(), name='bin'):
        self.command = [str(x) for x in ensure_iterable(command)]
        self.process = None
        self.running = False
        self.stdout = PIPE
        self.stderr = PIPE
        self.returncode = None
        super(BinExecutor, self).__init__(name)

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
    def __init__(self, name, *args):
        super(ParallelProcesses, self).__init__(name)
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
    def __init__(self, name, pbar=True, indent=False, *args):
        super(SequentialProcesses, self).__init__(name)
        self.pbar = pbar
        self.threads = list()
        self.threads.extend(args)
        self.thread_name_property = False
        self.stop_on_error = False
        self.returncode = None
        self.indent = indent

    def add(self, thread):
        self.threads.append(thread)

    def run(self):
        total = len(self.threads)
        rcs = [None]
        pc = None

        if self.indent:
            Printer.open()

        if self.pbar:
            if self.thread_name_property:
                pc = ProgressCounter('{self.name}: {:02d} of {total:02d} | {t.name}')
            else:
                pc = ProgressCounter('{self.name}: {:02d} of {total:02d}')

        for t in self.threads:
            if self.pbar:
                pc.next(locals())

            t.start()
            t.join()
            rc = getattr(t, 'returncode', None)
            rcs.append(rc)

            if self.stop_on_error and rc > 0:
                # Printer.out('Aborted next operations due to error')
                break

        self.returncode = max(rcs)
        super(SequentialProcesses, self).run()

        if self.indent:
            Printer.close()


class ParallelRunner(object):
    """
    :type threads: list[scripts.execs.test_executor.ExtendedThread]
    """
    def __init__(self, n=4):
        self.n = n if type(n) is int else 1
        self.i = 0
        self.threads = list()
        self.printer = Printer(Printer.LEVEL_KEY)

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

        pc = ProgressCounter('Case {:02d} of {total:02d}')
        while self.i < total:
            while self.active_count() < self.n:
                pc.next(locals())
                self.threads[self.i].start()
                self.i += 1

                # no more processes
                if self.i >= total:
                    break
                # sleep a bit to other threads can be active again
                time.sleep(0.1)
            time.sleep(0.1)

    def __repr__(self):
        return '<ParallelRunner x {self.n}>'.format(self=self)


class FD(object):
    def __init__(self):
        self.data = ''

    def write(self, data=''):
        self.data = data[:-1] if data.endswith('\r') else data
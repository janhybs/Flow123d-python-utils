#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
import threading, time, sys, psutil
from psutil import NoSuchProcess
from scripts.execs.test_executor import BrokenProcess
from utils.globals import apply_to_all, wait_for
from progressbar import ProgressBar, Timer, AnimatedMarker


class ProcessMonitor(threading.Thread):
    """
    :type monitors: list[AbstractMonitor]
    """
    def __init__(self, executor, period=.1):
        """
        :type executor: BinExecutor
        """
        super(ProcessMonitor, self).__init__()
        self.executor = executor
        self.period = period
        self.monitors = []

        self.limit_monitor = LimitMonitor(self)
        self.info_monitor = InfoMonitor(self)
        self.progress_monitor = ProgressMonitor(self)

        self.add_monitor(self.info_monitor)
        self.add_monitor(self.progress_monitor)
        self.add_monitor(self.limit_monitor)
        self.broken_process = False

    def add_monitor(self, monitor):
        self.monitors.append(monitor)

    def run(self):
        # start executions
        self.executor.start()

        # and wait for process to be created
        wait_for(self.executor, 'process')
        if type(self.executor.process) is BrokenProcess:
            self.broken_process = True

            self.info_monitor.start()
            print 'Process is broken: {}'.format(self.executor.process.exception)
            self.info_monitor.stop()
            return

        # start all monitors
        apply_to_all(self.monitors, 'start')

        # wait a bit so other threads can start
        self.sleep()
        # wait for the end
        while True:
            if not self.executor.process.is_running():
                break
            apply_to_all(self.monitors, 'update')
            self.sleep()

        # stop all monitors
        apply_to_all(reversed(self.monitors), 'stop')

    def sleep(self):
        time.sleep(self.period)


class AbstractMonitor(object):
    def __init__(self, process_monitor):
        """
        :type process_monitor: ProcessMonitor
        """
        self.process_monitor = process_monitor

    def start(self):
        pass

    def stop(self):
        pass

    def update(self):
        pass


class ExtendedTimer(Timer):
    def __init__(self, limit_monitor):
        """
        :type limit_monitor: scripts.execs.monitor.LimitMonitor
        """
        super(ExtendedTimer, self).__init__()
        self.limit_monitor = limit_monitor

    def update(self, pbar):
        runtime = self.limit_monitor.get_runtime() or pbar.seconds_elapsed
        if not pbar.finished:
            return 'Elapsed Time: {}'.format(Timer.format_time(int(runtime)))

        base = Timer.format_time(int(runtime))
        millis = '{:0.3f}'.format(runtime - int(runtime))
        return 'Elapsed Time: {}:{}'.format(base, millis[2:])


class ProgressMonitor(AbstractMonitor):
    def __init__(self, process_monitor):
        """
        :type process_monitor: scripts.execs.monitor.ProcessMonitor
        """
        widgets = ['Running ', AnimatedMarker(), ' (', ExtendedTimer(process_monitor.limit_monitor), ')']
        super(ProgressMonitor, self).__init__(process_monitor)
        self.progress_bar = ProgressBar(widgets=widgets, maxval=100, fd=sys.stdout)

    def start(self):
        super(ProgressMonitor, self).start()
        self.progress_bar.start()

    def stop(self):
        super(ProgressMonitor, self).stop()
        self.progress_bar.finish()

    def update(self):
        super(ProgressMonitor, self).update()
        self.progress_bar.update(0)


class InfoMonitor(AbstractMonitor):
    def __init__(self, process_monitor):
        super(InfoMonitor, self).__init__(process_monitor)

    def start(self):
        print 'Executing: {}'.format(' '.join(self.process_monitor.executor.command))

    def stop(self):
        wait_for(self.process_monitor.executor.process, 'returncode')
        print 'Command ({process.pid}) ended with {process.returncode}'.format(
            process=self.process_monitor.executor.process)
        print '-' * 60


class Limits(object):
    def __init__(self, time_limit=None, memory_limit=None):
        self.time_limit = time_limit
        self.memory_limit = memory_limit


class LimitMonitor(AbstractMonitor):
    """
    :type process: psutil.Process
    """
    def __init__(self, process_monitor):
        super(LimitMonitor, self).__init__(process_monitor)
        self.process = None
        self.memory_limit = None
        self.time_limit = None
        self.monitor_thread = None
        self.terminated = False
        self.terminated_cause = None

    def set_limits(self, limits):
        """
        :type limits: Limits
        """
        # empty Limits object
        if not limits:
            limits = Limits()

        self.memory_limit = limits.memory_limit
        self.time_limit = limits.time_limit

    def start(self):
        print 'Limits: time-limit: {self.time_limit_str} | memory-limit: {self.memory_limit_str}'.format(self=self)
        wait_for(self.process_monitor.executor, 'process')
        wait_for(self.process_monitor.executor.process, 'pid')
        self.process = psutil.Process(self.process_monitor.executor.process.pid)

    def update(self):
        self.check_limits()

    def get_runtime(self):
        try:
            return time.time() - self.process.create_time()
        except psutil.NoSuchProcess as e1:
            # process has ended
            return 0
        except AttributeError as e2:
            # process did not start
            return 0

    def get_memory_usage(self):
        try:
            return self.process.memory_info().vms / (1024.**2)
        except psutil.NoSuchProcess:
            # process has ended
            return 0

    def terminate(self):
        try:
            self.process.terminate()
        except NoSuchProcess:
            pass
        try:
            self.process.kill()
        except NoSuchProcess:
            pass

    def check_limits(self):
        if self.terminated:
            return

        if self.time_limit:
            runtime = self.get_runtime()
            if runtime > self.time_limit:
                print 'Error: Process is running longer then expected {:1.2f}s used, {:1.2f}s allowed'.format(
                    runtime, self.time_limit
                )
                self.terminate()
                self.terminated_cause = 'TIME_LIMIT'
                self.terminated = True

        if self.memory_limit:
            memory_usage = self.get_memory_usage()
            if memory_usage > self.memory_limit:
                print 'Error: Memory usage exceeded limit! {:1.2f}MB used, {:1.2f}MB allowed'.format(
                    memory_usage, self.memory_limit
                )
                self.terminate()
                self.terminated_cause = 'MEMORY_LIMIT'
                self.terminated = True

    @property
    def time_limit_str(self):
        if self.time_limit:
            return '{:1.2f}s'.format(self.time_limit)

    @property
    def memory_limit_str(self):
        if self.memory_limit:
            return '{:1.2f}MB'.format(self.memory_limit)
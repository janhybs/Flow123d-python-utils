#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
import threading, time
import sys
import psutil
from utils.globals import apply_to_all, wait_for


class ProcessMonitor(threading.Thread):
    """
    :type monitors: list[AbstractMonitor]
    """
    def __init__(self, executor, period=.5):
        """
        :type executor: Executor
        """
        super(ProcessMonitor, self).__init__()
        self.executor = executor
        self.period = period
        self.monitors = []
        self.add_monitor(InfoMonitor(self))
        self.add_monitor(ProgressMonitor(self))

    def add_monitor(self, monitor):
        self.monitors.append(monitor)

    def run(self):
        self.executor.start()
        # start all monitors
        apply_to_all(self.monitors, 'start')

        self.sleep()
        # wait for the end
        while True:
            if not self.executor.process:
                # process does not exists yet
                pass
            elif not self.executor.process.is_running():
                break

            self.sleep()
            apply_to_all(self.monitors, 'update')

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


class ProgressMonitor(AbstractMonitor):
    def __init__(self, process_monitor):
        from progressbar import ProgressBar, Timer, AnimatedMarker

        widgets = ['Running ', AnimatedMarker(), ' (', Timer(), ')']
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


class LimitMonitor(AbstractMonitor):
    """
    :type process: psutil.Process
    """
    def __init__(self, process_monitor):
        super(LimitMonitor, self).__init__(process_monitor)
        self.process = None
        self.limit_memory = None
        self.limit_runtime = None
        self.monitor_thread = None
        self.terminated = False
        self.terminated_cause = None

    def start(self):
        wait_for(self.process_monitor.executor, 'process')
        wait_for(self.process_monitor.executor.process, 'pid')
        self.process = psutil.Process(self.process_monitor.executor.process.pid)

    def update(self):
        self.check_limits()

    def get_runtime(self):
        return time.time() - self.process.create_time()

    def get_memory_usage(self):
        return self.process.memory_info().vms / (1024.**2)

    def check_limits(self):
        if self.limit_runtime:
            if self.get_runtime() > self.limit_runtime:
                print 'Process is running longer then expected'
                self.process.kill()
                return True
        if self.limit_memory:
            if self.get_memory_usage() > self.limit_memory:
                print 'Memory usage exceeded limit'
                self.process.kill()
                return True

    def monitor(self):
        def target():
            while True:
                if self.check_limits():
                    self.terminated = True
                    self.terminated_cause = "RUNTIME-LIMIT"
                    break
                time.sleep(1)

        self.monitor_thread = threading.Thread(target=target)
        self.monitor_thread.start()

    def info(self):
        # while True:
            print self.get_runtime()

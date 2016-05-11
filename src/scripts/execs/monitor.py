#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
import threading, time
import sys
from utils.globals import apply_to_all


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
        print 'Command ({process.pid}) ended with {process.returncode}'.format(
            process=self.process_monitor.executor.process)
        print '-' * 60
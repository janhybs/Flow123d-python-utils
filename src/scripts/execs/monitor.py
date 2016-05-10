#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
import threading, time
from utils.globals import apply_to_all


class ProcessMonitor(threading.Thread):
    """
    :type monitors: list[AbstractMonitor]
    """
    def __init__(self, executor, period=0.2):
        """
        :type executor: Executor
        """
        super(ProcessMonitor, self).__init__()
        self.executor = executor
        self.period = period
        self.monitors = []

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
        apply_to_all(self.monitors, 'stop')

    def sleep(self):
        time.sleep(self.period)


class AbstractMonitor(object):
    def start(self):
        pass

    def stop(self):
        pass

    def update(self):
        pass


class ProgressMonitor(AbstractMonitor):
    def __init__(self):
        from progressbar import ProgressBar, Timer, AnimatedMarker

        widgets = ['Running ', AnimatedMarker(), ' (', Timer(), ')']
        super(ProgressMonitor, self).__init__()
        self.progress_bar = ProgressBar(widgets=widgets, maxval=100)

    def start(self):
        super(ProgressMonitor, self).start()
        self.progress_bar.start()

    def stop(self):
        super(ProgressMonitor, self).stop()
        self.progress_bar.finish()

    def update(self):
        super(ProgressMonitor, self).update()
        self.progress_bar.update(0)
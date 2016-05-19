#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import subprocess


class JobState(object):
    COMPLETED = 'C'
    EXITING = 'E'
    HELD = 'H'
    QUEUED = 'Q'
    RUNNING = 'R'
    TRANSFER = 'T'
    WAITING = 'W'
    SUSPENDED = 'S'
    UNKNOWN = 'U'
    COMPLETED_OK = 'K'
    COMPLETED_ERROR = 'W'
    _map = {}

    def __init__(self, value='U'):
        if not JobState._map:
            JobState._map = {v[0]: v for v in dir(JobState) if v.upper() == v}
        self.value = str(value).upper()

    def __eq__(self, other):
        if type(other) is JobState:
            return self.value == other.value
        return self.value == str(other).upper()

    def __ne__(self, other):
        if type(other) is JobState:
            return self.value != other.value
        return self.value != str(other).upper()

    def __bool__(self):
        return self.value == self.COMPLETED
    __nonzero__=__bool__

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "{enum}".format(cls=self.__class__.__name__, enum=JobState._map.get(self.value))

    def enum(self):
        return self.value


class Job(object):
    def __init__(self, job_id, output_file):
        self.id = job_id
        self.output_file = output_file

        self.name = None
        self.queue = None
        self.last_status = JobState(JobState.UNKNOWN)
        self.status_changed = False
        self.parser = lambda x: None
        self.active = True
        self._status = JobState(JobState.UNKNOWN)

    @property
    def status(self):
        """
        :rtype : scripts.pbs.job.JobState
        """
        return self._status
    
    @status.setter
    def status(self, value):
        """
        :type value: scripts.pbs.job.JobState or str
        """
        if type(value) is not JobState:
            value = JobState(value)

        # set state
        self._status = value
        self.status_changed = self.last_status != self._status
        self.last_status = self._status

    def update_status(self, output):
        if self.active:
            self.status = self.parse_status(output)

    def raise_not_found(self):
        raise Exception('Job with id {self.id} does not exists'.format(self=self))

    def __repr__(self):
        return "<Job #{s.id}, status {s.status} in queue {s.queue}>".format(s=self)

    # --------------------------------------------------------

    @classmethod
    def update_command(cls):
        """
        :rtype : list[str]
        """
        raise NotImplementedError('Method not implemented!')

    def parse_status(self, output=""):
        """
        :rtype : str
        """
        return self.parser(output)

    @classmethod
    def create(cls, output, output_file):
        """
        Creates instance of Job from qsub output
        :param output: output of qsub command
        """
        raise NotImplementedError('Method not implemented!')

    @classmethod
    def parser_builder(cls, o, index, default=JobState.UNKNOWN, **kwargs):
        def parse(output):
            for line in output.splitlines():
                if line.find(o.id) != -1:
                    info = line.split()
                    for name, i in kwargs.items():
                        setattr(o, name, info[i])
                    return info[index]
            return default
        return parse


class MultiJob(object):
    """
    :type items             : list[scripts.pbs.job.Job]
    :type cls               : class
    """
    def __init__(self, cls):
        self.items = list()
        self.cls = cls
        self._iter_index = 0

    def __iter__(self):
        self.iter_index = 0
        return self

    def next(self):
        """
        :rtype : scripts.pbs.job.Job
        """
        if self._iter_index >= len(self.items):
            raise StopIteration
        else:
            self._iter_index += 1
            return self.items[self._iter_index - 1]

    __next__ = next

    def add(self, *items):
        self.items.extend(items)

    def status(self):
        return {item: item.status for item in self.items}

    def update(self):
        output = subprocess.check_output(self.cls.update_command())
        return [item.update_status(output) for item in self.items]

    def is_running(self):
        status = set(self.status().values())
        status = status - {JobState.COMPLETED_OK, JobState.COMPLETED_ERROR}
        return bool(status)

    def print_status(self, printer):
        """
        :type printer: scripts.core.base.Printer
        """
        for item in self.items:
            printer.key(str(item))

    def status_changed(self):
        """
        :rtype : list[scripts.pbs.job.Job]
        """
        return [item for item in self.items if item.status_changed]

    def get_status_line(self):
        status = self.status().values()
        result = dict()

        for s in set(status):
            result[s] = status.count(s)

        return ', '.join(['{}: {:02d}'.format(k, v) for k, v in result.items()])

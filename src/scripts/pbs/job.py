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
    _map = None

    def __init__(self, value='U'):
        if not JobState._map:
            JobState._map = { v[0]: v for v in dir(JobState) if v.upper() == v }
        self.value = str(value).upper()

    def __eq__(self, other):
        if type(other) is JobState:
            return self.value == other.value
        return self.value == str(other).upper()

    def __ne__(self, other):
        if type(other) is JobState:
            return self.value != other.value
        return self.value != str(other).upper()

    def __repr__(self):
        return "{enum}".format(cls=self.__class__.__name__, enum=JobState._map.get(self.value))

    def enum(self):
        return self.value


class Job(object):
    def __init__(self, job_id):
        self.id = job_id
        self.name = None
        self.owner = None
        self.cpu = None
        self.queue = None
        self.prior = None
        self.date = None
        self.time = None
        self.slots = None
        self.state = JobState(JobState.UNKNOWN)

    def update_status(self):
        state = self.parse_status(subprocess.check_output(self.update_command()))
        self.state = JobState(state)

    def status(self):
        return self.state

    def raise_not_found(self):
        raise Exception('Job with id {self.id} does not exists'.format(self=self))

    def __repr__(self):
        return "<Job #{s.id}, status {s.state} in queue {s.queue}>".format(s=self)

    # --------------------------------------------------------

    @classmethod
    def update_command(cls):
        raise NotImplementedError('Method not implemented!')

    def parse_status(self, output=""):
        raise NotImplementedError('Method not implemented!')

    @classmethod
    def create(cls, output=""):
        """
        Creates instance of Job from qsub output
        :param output: output of qsub command
        """
        raise NotImplementedError('Method not implemented!')
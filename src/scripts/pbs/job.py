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
        return self.value == str(other).upper()

    def __ne__(self, other):
        return self.value != str(other).upper()

    def __repr__(self):
        return "{enum}".format(cls=self.__class__.__name__, enum=JobState._map.get(self.value))


class Job(object):
    def __init__(self, job_id):
        self.id = job_id
        self.name = None
        self.owner = None
        self.cpu = None
        self.queue = None
        self.state = JobState()

    def update_status(self):
        output = subprocess.check_output(['qstat', self.id])
        status_lines = output.split('\n')
        if len(status_lines) < 2:
            self.state = JobState(JobState.UNKNOWN)
            raise Exception('Job with id {self.id} does not exists'.format(self=self))

        status_line = status_lines[2].split()
        self.id, self.name, self.owner, self.cpu, self.state, self.queue = status_line
        self.state = JobState(self.state)

    def __repr__(self):
        return "<Job #{self.id}, status {self.state}>".format(self=self)
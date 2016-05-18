#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from scripts.core.prescriptions import PBSModule
from scripts.pbs.job import Job, JobState

import re

class Module(PBSModule):
    def get_pbs_command(self, options, pbs_script_filename):
        # total parallel process
        np = self.proc_value
        # processes per node, default value 2 (Master-slave)
        ppn = options.get('ppn', 2)

        # command
        command = [
            'qsub',
            '-pe', 'orte', '{np}'.format(**locals()),
            '-l', 'num_proc={ppn}'.format(**locals()),
            pbs_script_filename
        ]

        return command


class ModuleJob(Job):
    def __init__(self, job_id):
        super(ModuleJob, self).__init__(job_id)

    def parse_status(self, output=""):
        for line in output.splitlines():
            if line.find(self.id) != -1:
                id, self.prior, self.name, self.user, self.state, \
                self.date, self.time, self.queue, self.slots = line.split()
                self.state = JobState(self.state)
                return self.state

        self.state = JobState(JobState.COMPLETED)
        return self.state

    @classmethod
    def update_command(cls):
        return ['qstat']

    @classmethod
    def create(cls, output=""):
        return ModuleJob(re.findall(r'(\d+)', output)[0])

template = """
#!/bin/bash
#
#$ -cwd
#$ -j y
#$ -S /bin/bash

# Disable system rsh / ssh only
# export OMPI_MCA_plm_rsh_disable_qrsh=1

#################

ROOT="$$root$$"

echo "$$command$$"
# $$command$$

""".lstrip()
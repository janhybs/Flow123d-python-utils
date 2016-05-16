#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import math
from scripts.core.base import Printer
from scripts.core.prescriptions import PBSModule
from scripts.pbs.job import Job


class Module(PBSModule):
    def get_pbs_command(self, options, pbs_script_filename):
        # total parallel process
        np = self.proc_value
        # processes per node, default value 1
        ppn = options.get('ppn', 1)
        # number of physical machines to be reserved
        nodes = float(np) / ppn
        if int(nodes) != nodes:
            Printer.err('Warning: NP is not divisible by PPN')
        nodes = int(math.ceil(nodes))

        # memory limit
        mem = int(self.test_case.memory_limit * ppn)

        # get queue, if only -q is set, 'default' queue will be set
        # otherwise given string value will be used
        queue = options.get('queue', 'default')
        queue = 'default' if queue is True else queue

        # command
        command = [
            'qsub',
            '-l', 'nodes={nodes}:ppn={ppn}'.format(**locals()), # :nfs4 option may be set
            '-l', 'mem={mem}mb'.format(**locals()),
            '-l', 'place=infiniband',
            '-q', '{queue}'.format(**locals()),
            pbs_script_filename
        ]

        return command


class ModuleJob(Job):
    def __init__(self, job_id):
        super(ModuleJob, self).__init__(job_id)

    def update_command(self):
        return ['qstat', self.id]

    def parse_status(self, output=""):
        lines = output.splitlines()
        if len(lines) < 2:
            self.raise_not_found()

        self.id, self.name, self.owner, self.cpu, self.state, self.queue = lines[2].split()
        return self.state


template = """
#!/bin/bash
#
# Specific PBS setting
#
#PBS -S /bin/bash
#PBS -N flow123d
#PBS -j oe

# load modules
#################
module purge
module add /software/modules/current/metabase
module add svn-1.7.6
module add intelcdk-12
module add boost-1.49
module add mpich-p4-intel
module add cmake-2.8
module add python-2.6.2
module unload mpiexec-0.84
module unload mpich-p4-intel
module add openmpi-1.6-intel
module add gcc-4.7.0
module add perl-5.10.1

module add python26-modules-gcc
module add numpy-py2.6
module add python-2.7.6-gcc
moduel add
#################



cd ${WORKDIR}

# header - info about task
uname -a
echo JOB START: `date`
pwd

echo "$$command$$"
$$command$$

""".lstrip()
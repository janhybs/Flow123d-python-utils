#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import math
from scripts.core.base import Printer
from scripts.core.prescriptions import PBSModule


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

# OPTIONS="-l nodes=${NNodes}:ppn=${PPN}:x86_64:nfs4:debian60 -l mem=${MEM}mb ${SET_WALLTIME} ${UNRESOLVED_PARAMS} -q ${QUEUE}"
# Add new PBS job to the queue
# echo "qsub ${OPTIONS} ${QSUB_FILE}"

# NP is number of procs used to compute
# MPIEXEC is relative path to bin/mpiexec
# FLOW123D is relative path to bin/flow123d (.exe)
# FLOW_PARAMS is list of parameters of flow123d
# INI_FILE is name of .ini file
# WORKDIR is directory from which flow123d.sh was started
# TIMEOUT is max time to run
#
# sets variable STDOUT_FILE to the file name of the joined redirected stdout and stderr
#
# * the job is started from /storage/.../home/USER/...

# Some important files
# export ERR_FILE="err.log"
# export OUT_FILE="out.log"
#
# QSUB_FILE="/tmp/${USER}-flow123.qsub"
#     rm -f ${QSUB_FILE}
#
# if [ -z "${QUEUE}" ]; then QUEUE=normal; fi
# if [ -z "${PPN}" ]; then PPN=2; fi
# if [ -z "${MEM}" ]; then MEM="$(( ${PPN} * 2))"; fi
# # divide and round up
# NNodes="$(( ( ${NP} + ${PPN} -1 ) / ${PPN} ))"
# if [ -n "${TIMEOUT}" ]; then SET_WALLTIME="-l walltime=${TIMEOUT}";fi

# echo "    --host HOSTNAME               Use given HOSTNAME for backend script resolution. Script 'config/\${HOSTNAME}.sh' must exist."
# echo "    -t, --walltime TIMEOUT        Specifies a maximum time period after which Flow123d will be killed.  Time TIMEOUT is expressed in seconds as an integer,\n or in the form: [[hours:]minutes:]seconds[.milliseconds]."
# echo "    -m, --mem MEM                 Flow123d can use only MEM magabytes per process."
# echo "    -n, --nice NICE               Run Flow123d with changed (lower) priority."
# echo "    -np N                         Run Flow123d using N parallel processes."
# echo "    -ppn PPN                      Run PPN processes per node. NP should be divisible by PPN other wise it will be truncated."
# echo "    -q, --queue QUEUE             Name of queue to use for batch processing. For interactive runs this redirect stdout and stderr to the file with name in format QUEUE.DATE."


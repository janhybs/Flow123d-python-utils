#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from scripts.core.prescriptions import PBSModule


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
            # '-l', 'num_proc={ppn}'.format(**locals()),
            pbs_script_filename
        ]

        return command

template = """
#!/bin/bash
#
#$ -cwd
#$ -j y
#$ -S /bin/bash

# Disable system rsh / ssh only
export OMPI_MCA_plm_rsh_disable_qrsh=1

#################

echo "$$command$$"
$$command$$

""".lstrip()
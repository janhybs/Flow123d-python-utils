#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from scripts.core.base import Paths, Printer, CommandEscapee, IO
from scripts.core.base import PathFormat
from scripts.core.prescriptions import PBSModule
from scripts.execs.monitor import ProcessMonitor
from scripts.execs.test_executor import BinExecutor
from scripts.pbs.common import get_pbs_module
import subprocess, time, datetime

# global arguments
from scripts.pbs.job import JobState
from utils.dotdict import Map

arg_options = None
arg_others = None
arg_rest = None


def run_local_mode():
    # build command
    mpi_binary = 'mpirun' if arg_options.mpirun else Paths.mpiexec()
    command = [
        mpi_binary,
        '-np', str(arg_options.get('cpu', 1))
    ]
    # append rest arguments
    command.extend(arg_rest)

    # prepare executor
    executor = BinExecutor(command)
    process_monitor = ProcessMonitor(executor)

    # set limits
    process_monitor.limit_monitor.time_limit = arg_options.time_limit
    process_monitor.limit_monitor.memory_limit = arg_options.memory_limit

    # start process
    process_monitor.start()


def run_pbs_mode():
    # build command
    mpi_binary = 'mpirun' if arg_options.mpirun else Paths.mpiexec()
    command = [
        mpi_binary,
        '-np', str(arg_options.get('cpu', 1))
    ]
    # append rest arguments
    command.extend(arg_rest)

    # get module
    pbs_module = get_pbs_module(arg_options.host)

    # create pbs command
    test_case = Map(
        memory_limit=arg_options.memory_limit
    )
    module = pbs_module.Module(test_case, arg_options.cpu, None)
    temp_file = Paths.temp_file('exec-temp.qsub')
    pbs_command = module.get_pbs_command(arg_options, temp_file)

    # create regular command for execution
    escaped_command = ' '.join(CommandEscapee.escape_command(command))

    # create pbs script
    pbs_content = PBSModule.format(
        pbs_module.template,
        command=escaped_command,
        root=arg_options.root
    )

    # print debug info
    Printer.out('Command : {}', escaped_command)
    Printer.out('PBS     : {}', pbs_command)
    Printer.out('script  : {}', temp_file)

    # save pbs script
    IO.write(temp_file, pbs_content)

    # run qsub command
    output = subprocess.check_output(pbs_command)
    start_time = time.time()
    job = pbs_module.ModuleJob.create(output)
    job.update_status()
    Printer.out('Job submitted: {}', job)

    # wait for job to end
    while job.state != JobState.COMPLETED:
        job.update_status()
        elapsed = time.time() - start_time
        elapsed_str = str(datetime.timedelta(seconds=int(elapsed)))

        Printer.out_rr(' ' * 60)
        Printer.out_rr('Job #{job.id} status: {job.state} ({t})', job=job, t=elapsed_str)

        if job.state == JobState.COMPLETED:
            break

        # sleep for a bit
        time.sleep(3)
    Printer.out('\nJob ended')

    # delete tmp file
    # IO.delete(temp_file)


def do_work(frontend_file, parser):
    """
    :type frontend_file: str
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    global arg_options, arg_others, arg_rest
    arg_options, arg_others, arg_rest = parser.parse()
    Paths.format = PathFormat.ABSOLUTE

    # check commands
    if not arg_rest:
        parser.exit_usage('No command specified!')

    # check root
    if not arg_options.root:
        # try to find our root
        arg_options.root = Paths.join(Paths.dirname(frontend_file), '..', '..')
        Printer.out('Argument --root not specified, assuming root is {}', arg_options.root)

    # make root absolute
    arg_options.root = Paths.abspath(arg_options.root)
    # change dir to root
    Paths.base_dir(arg_options.root)

    # run local or pbs mode
    if arg_options.queue:
        Printer.out('Running in PBS mode')
        run_pbs_mode()
    else:
        Printer.out('Running in LOCAL mode')
        run_local_mode()

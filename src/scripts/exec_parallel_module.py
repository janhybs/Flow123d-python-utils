#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
# ----------------------------------------------
import subprocess
import datetime
import time
# ----------------------------------------------
import sys

from scripts.config.yaml_config import ConfigCase, DEFAULTS
from scripts.core.base import Paths, Printer, Command, IO, GlobalResult
from scripts.core.base import PathFormat
from scripts.core.threads import PyPy
from scripts.core.execution import BinExecutor, OutputMode
from scripts.pbs.common import get_pbs_module, job_ok_string
from scripts.pbs.job import JobState, finish_pbs_job, MultiJob
from scripts.prescriptions.remote_run import exec_parallel_command, PBSModule
from utils.counter import ProgressCounter
from utils.dotdict import Map
# ----------------------------------------------

# global arguments
from utils.globals import ensure_iterable
from utils.strings import format_n_lines

arg_options = None
arg_others = None
arg_rest = None
debug_mode = False

#
# def run_local_mode():
#     """
#     :rtype: scripts.core.threads.PyPy or int
#     """
#     global arg_options, arg_others, arg_rest, debug_mode
#     # build command
#     mpi_binary = 'mpirun' if arg_options.mpirun else Paths.mpiexec()
#     command = [
#         mpi_binary,
#         '-np', str(arg_options.get('cpu', 1))
#     ]
#     if arg_options.valgrind:
#         valgrind = ['valgrind']
#         if type(arg_options.valgrind) is str:
#             valgrind.extend(arg_options.valgrind.split())
#         # append to command
#         command = command + valgrind
#     # append rest arguments
#     command.extend(arg_rest)
#
#     # prepare executor
#     executor = BinExecutor(command)
#     pypy = PyPy(executor, progress=not arg_options.batch)
#
#     # set limits
#     pypy.limit_monitor.time_limit = arg_options.time_limit
#     pypy.limit_monitor.memory_limit = arg_options.memory_limit
#
#     # turn on output
#     if arg_options.batch:
#         pypy.info_monitor.stdout_stderr = None
#     else:
#         pypy.info_monitor.stdout_stderr = Paths.temp_file('exec-paral.log')
#
#     # start process
#     pypy.start()
#     pypy.join()
#
#     if debug_mode:
#         return pypy
#     return pypy.returncode
#
#
# def run_pbs_mode():
#     """
#     :rtype: scripts.core.threads.PyPy or int
#     """
#     global arg_options, arg_others, arg_rest, debug_mode
#     # build command
#     mpi_binary = 'mpirun' if arg_options.mpirun else Paths.mpiexec()
#     command = [
#         mpi_binary,
#         '-np', str(arg_options.get('cpu', 1))
#     ]
#     # append rest arguments
#     command.extend(arg_rest)
#
#     # get module
#     pbs_module = get_pbs_module(arg_options.host)
#
#     # create pbs command
#     test_case = Map(
#         memory_limit=arg_options.get('memory_limit', None) or 400,
#         time_limit=arg_options.get('time_limit', None) or 30
#     )
#     case = pbs_module.Module(test_case, arg_options.cpu, None)
#     pbs_command = case.get_pbs_command(arg_options, case.pbs_script)
#
#     # create regular command for execution
#     escaped_command = ' '.join(Command.escape_command(command))
#
#     # create pbs script
#     pbs_content = PBSModule.format(
#         pbs_module.template,
#         command=escaped_command,
#         root=case.output_dir,
#         output=case.job_output,
#         status_ok=job_ok_string,
#     )
#
#     # save pbs script
#     IO.write(case.pbs_script, pbs_content)
#
#     # run qsub command
#     output = subprocess.check_output(pbs_command)
#     start_time = time.time()
#     job = pbs_module.ModuleJob.create(output, case)
#     job.full_name = "MPI exec job"
#
#     multijob = MultiJob(pbs_module.ModuleJob)
#     multijob.add(job)
#
#     Printer.dyn('Updating job status...')
#     multijob.update()
#     Printer.out('Job submitted: {}', job)
#
#     # wait for job to end
#     while job.status != JobState.COMPLETED:
#         for j in range(6):
#             elapsed_str = str(datetime.timedelta(seconds=int(time.time() - start_time)))
#             Printer.dyn('Job #{job.id} status: {job.state} ({t})', job=job, t=elapsed_str)
#
#             # test job status
#             if job.status == JobState.COMPLETED:
#                 break
#
#             # sleep for a bit
#             time.sleep(0.5)
#
#         # update status every 6 * 0.5 seconds (3 sec update)
#         multijob.update()
#
#     returncode = finish_pbs_job(job, arg_options.batch)
#     if debug_mode:
#         return job
#     return returncode


def create_pbs_job_content(module, case):
    """
    :type case: scripts.config.yaml_config.ConfigCase
    :type module: scripts.pbs.modules.pbs_tarkil_cesnet_cz
    :rtype : str
    """

    import pkgutil

    command = PBSModule.format(
        exec_parallel_command,

        python=sys.executable,
        script=pkgutil.get_loader('exec_parallel').filename,
        limits="-n {case.proc} -m {case.memory_limit} -t {case.time_limit}".format(case=case),
        args="" if not arg_rest else Command.to_string(arg_rest),
        json_output=case.fs.json_output
    )

    template = PBSModule.format(
        module.template,
        command=command,
        json_output=case.fs.json_output # TODO remove
    )

    return template


def prepare_pbs_files(pbs_module):
    """
    :type pbs_module: scripts.pbs.modules.pbs_tarkil_cesnet_cz
    :rtype: list[(str, PBSModule)]
    """

    proc, time_limit, memory_limit = get_args()

    jobs = list()

    for p in proc:
        case = ConfigCase(dict(
            proc=p,
            time_limit=time_limit,
            memory_limit=memory_limit,
            tmp='exec-parallel'
        ), None)

        pbs_run = pbs_module.Module(case)
        pbs_run.queue = arg_options.get('queue', True)
        pbs_run.ppn = arg_options.get('ppn', 1)

        pbs_content = create_pbs_job_content(pbs_module, case)
        IO.write(case.fs.pbs_script, pbs_content)

        qsub_command = pbs_run.get_pbs_command(case.fs.pbs_script)
        jobs.append((qsub_command, pbs_run))
    return jobs


def run_pbs_mode(debug=False):
    pbs_module = get_pbs_module()
    jobs = prepare_pbs_files(pbs_module)

    if debug:
        return 0

    # start jobs
    Printer.dyn('Starting jobs')

    total = len(jobs)
    job_id = 0
    multijob = MultiJob(pbs_module.ModuleJob)
    for qsub_command, pbs_run in jobs:
        job_id += 1

        Printer.dyn('Starting jobs {:02d} of {:02d}', job_id, total)

        output = subprocess.check_output(qsub_command)
        job = pbs_module.ModuleJob.create(output, pbs_run.case)
        job.full_name = "Case {}".format(pbs_run.case)
        multijob.add(job)

    Printer.out()
    Printer.out('{} job/s inserted into queue', total)

    # # first update to get more info about multijob jobs
    Printer.out()
    Printer.separator()
    Printer.dyn('Updating job status')
    multijob.update()

    # print jobs statuses
    Printer.out()
    if not arg_options.batch:
        multijob.print_status()

    Printer.separator()
    Printer.dyn(multijob.get_status_line())
    returncodes = dict()

    # wait for finish
    while multijob.is_running():
        Printer.dyn('Updating job status')
        multijob.update()
        Printer.dyn(multijob.get_status_line())

        # if some jobs changed status add new line to dynamic output remains
        jobs_changed = multijob.get_all(status=JobState.COMPLETED)
        if jobs_changed:
            Printer.out()
            Printer.separator()

        # get all jobs where was status update to COMPLETE state
        for job in jobs_changed:
            returncodes[job] = finish_pbs_job(job, arg_options.batch)

        if jobs_changed:
            Printer.separator()
            Printer.out()

        # after printing update status lets sleep for a bit
        if multijob.is_running():
            time.sleep(5)

    Printer.out(multijob.get_status_line())
    Printer.out('All jobs finished')

    # get max return code or number 2 if there are no returncodes
    return max(returncodes.values()) if returncodes else 2


def run_local_mode_one(proc, time_limit, memory_limit):
    if proc == 0:
        command = arg_rest[1:]
    else:
        command = [arg_rest[0], '-np', proc] + arg_rest[1:]

    n_lines = 0 if arg_options.batch else 10
    pypy = PyPy(BinExecutor(command))

    # set limits
    pypy.limit_monitor.time_limit = time_limit
    pypy.limit_monitor.memory_limit = memory_limit
    pypy.progress = not arg_options.batch
    pypy.info_monitor.deactivate()
    pypy.error_monitor.deactivate()

    # catch output to variable
    # in batch mode we will keep the files
    # otherwise we will keep logs only on error
    log_file = Paths.temp_file('exec-parallel-{date}-{time}-{rnd}.log')
    pypy.executor.output = OutputMode.variable_output()
    pypy.full_output = log_file

    # start and wait for exit
    pypy.start()
    pypy.join()

    # add result to global json result
    GlobalResult.add(pypy)

    # in batch mode or on error
    if not pypy.with_success() or arg_options.batch:
        content = pypy.executor.output.read()
        IO.write(log_file, content)
        Printer.close()
        Printer.out(format_n_lines(content, indent='    ', n_lines=-n_lines))
        Printer.open()
    return pypy


def get_args():
    global arg_options, arg_others, arg_rest
    proc = ensure_iterable(arg_options.get('cpu'))
    time_limit = arg_options.get('time_limit')
    memory_limit = arg_options.get('memory_limit')

    # set default values if not set
    proc = proc if proc else DEFAULTS.get('proc')
    time_limit = time_limit if time_limit else DEFAULTS.get('time_limit')
    memory_limit = memory_limit if memory_limit else DEFAULTS.get('memory_limit')

    return proc, time_limit, memory_limit


def run_local_mode(debug=False):
    global arg_options, arg_others, arg_rest
    proc, time_limit, memory_limit = get_args()
    total = len(proc)

    if total == 1:
        pypy = run_local_mode_one(proc[0], time_limit, memory_limit)
        GlobalResult.returncode = pypy.returncode
    else:
        # optionally we use counter
        progress = ProgressCounter('Running {:02d} of {total:02d}')
        for p in proc:
            Printer.separator()
            progress.next(locals())
            Printer.separator()

            Printer.open()
            pypy = run_local_mode_one(p, time_limit, memory_limit)
            Printer.close()
            GlobalResult.returncode = max(GlobalResult.returncode, pypy.returncode)

    return GlobalResult.returncode if not debug else pypy


def do_work(parser, args=None, debug=False):
    """
    :type args: list
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    global arg_options, arg_others, arg_rest, debug_mode
    arg_options, arg_others, arg_rest = parser.parse(args)
    debug_mode = debug

    # configure path
    Paths.format = PathFormat.ABSOLUTE
    Paths.base_dir('' if not arg_options.root else arg_options.root)

    # check commands
    if len(arg_rest) == 0:
        parser.exit_usage('no MPI executable provided', exit_code=1)

    if len(arg_rest) == 1:
        parser.exit_usage('no executable provided', exit_code=2)

    # turn on dynamic messages if batch is not set
    Printer.dynamic_output = not arg_options.batch

    # # run local or pbs mode
    if arg_options.queue:
        return run_pbs_mode(debug)
    else:
        return run_local_mode(debug)
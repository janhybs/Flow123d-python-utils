#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
# ----------------------------------------------
import os
import subprocess
import time
import sys
# ----------------------------------------------
from scripts.config.yaml_config import ConfigPool
from scripts.core import prescriptions
from scripts.core.base import Paths, PathFormat, PathFilters, Printer, Command, IO, GlobalResult
from scripts.core.prescriptions import PBSModule
from scripts.core.threads import BinExecutor, ParallelThreads, SequentialThreads, PyPy
from scripts.pbs.common import get_pbs_module, job_ok_string
from scripts.pbs.job import JobState, MultiJob, finish_pbs_job
# ----------------------------------------------


# global arguments
from scripts.prescriptions.local_run import LocalRun

arg_options = None
arg_others = None
arg_rest = None


def create_process(command, limits=None):
    """
    :type command: list[str]
    :type limits: scripts.config.yaml_config.YamlConfigCase
    """
    command.extend(arg_rest)
    test_executor = BinExecutor(command)
    process_monitor = PyPy(test_executor)
    process_monitor.limit_monitor.set_limits(limits)
    return process_monitor


def create_process_from_case(case):
    """
    :type case: scripts.config.yaml_config.ConfigCase
    """
    local_run = LocalRun(case)
    local_run.mpi = case.proc > 1
    local_run.progress = not arg_options.batch

    seq = SequentialThreads('test-case', progress=False)

    seq.add(local_run.create_clean_thread())
    seq.add(local_run.create_pypy(arg_rest))
    seq.add(local_run.create_comparisons())

    seq.stop_on_error = True
    return seq


def create_pbs_job_content(module, case):
    """
    :type case: scripts.config.yaml_config.ConfigCase
    :type module: scripts.pbs.modules.pbs_tarkil_cesnet_cz
    :rtype : str
    """

    import pkgutil
    template = PBSModule.format(
        module.template,
        python=sys.executable,
        runtest=pkgutil.get_loader('runtest').filename,
        yaml=case.file,
        limits="-n {case.proc} -m {case.memory_limit} -t {case.time_limit}".format(
                case=case),
            args="" if not arg_rest else Command.to_string(arg_rest),
        json_output=case.fs.json_output
    )

    return template


def run_pbs_mode(configs, debug=False):
    """
    :type debug: bool
    :type configs: scripts.config.yaml_config.ConfigPool
    """
    global arg_options, arg_others, arg_rest
    pbs_module = get_pbs_module(arg_options.host)
    Printer.dyn_enabled = not arg_options.batch
    Printer.dyn('Parsing yaml files')

    jobs = list()
    """ :type: list[(str, PBSModule)] """

    for yaml_file, yaml_config in configs.files.items():
        for case in yaml_config.get_one(yaml_file):
            pbs_run = pbs_module.Module(case)
            pbs_run.queue = arg_options.get('queue', True)
            pbs_run.ppn = arg_options.get('ppn', 1)

            pbs_content = create_pbs_job_content(pbs_module, case)
            IO.write(case.fs.pbs_script, pbs_content)

            qsub_command = pbs_run.get_pbs_command(case.fs.pbs_script)
            jobs.append((qsub_command, pbs_run))

    # start jobs
    Printer.dyn('Starting jobs')

    total = len(jobs)
    job_id = 0
    multijob = MultiJob(pbs_module.ModuleJob)
    for qsub_command, pbs_run in jobs:
        pass
        job_id += 1

        Printer.dyn('Starting jobs {:02d} of {:02d}', job_id, total)

        output = subprocess.check_output(qsub_command)
        job = pbs_module.ModuleJob.create(output, case)
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
    returncode = max(returncodes.values()) if returncodes else 2
    sys.exit(returncode)


def run_local_mode(configs, debug=False):
    """
    :type debug: bool
    :type configs: scripts.config.yaml_config.ConfigPool
    """
    global arg_options, arg_others, arg_rest
    runner = ParallelThreads(arg_options.parallel)
    runner.stop_on_error = not arg_options.keep_going

    for yaml_file, yaml_config in configs.files.items():
        for case in yaml_config.get_one(yaml_file):
            # create main process which first clean output dir
            # and then execute test following with comparisons
            multi_process = create_process_from_case(case)
            runner.add(multi_process)

    # run!
    runner.start()
    while runner.is_running():
        time.sleep(1)

    Printer.separator()
    Printer.out('Summary: ')
    Printer.open()

    for thread in runner.threads:
        multithread = thread
        """ :type: SequentialThreads """

        clean = multithread.threads[0]
        """ :type: CleanThread """

        pypy = multithread.threads[1]
        """ :type: PyPy """

        comp = multithread.threads[2]
        """ :type: SequentialThreads """

        returncode = max([clean, pypy, comp])
        GlobalResult.add(multithread.threads)

        if not clean:
            Printer.out("[{:^6}]:{:3}| Could not clean directory '{}': {}",
                        'ERROR', clean.returncode, clean.dir, clean.error)
            continue

        if not pypy:
            Printer.out("[{:^6}]:{:3}| Run error, case: {}",
                        'ERROR', pypy.returncode, pypy.case.to_string())
            continue

        if not comp:
            Printer.out("[{:^6}]:{:3}| Compare error, case: {}, Details: ",
                        'FAILED', comp.returncode, pypy.case.to_string())
            Printer.open(2)
            for t in comp.threads:
                if t:
                    Printer.out('[{:^6}]: {}', 'OK', t.name)
                else:
                    Printer.out('[{:^6}]: {}', 'FAILED', t.name)
            Printer.close(2)
            continue

        Printer.out("[{:^6}]:{:3}| Test passed: {}",
                    'PASSED', pypy.returncode, pypy.case.to_string())
    Printer.close()

    # exit with runner's exit code
    GlobalResult.returncode = runner.returncode
    return runner if debug else runner.returncode


def read_configs(all_yamls):
    """
    :rtype: scripts.config.yaml_config.ConfigPool
    """
    configs = ConfigPool()
    for y in all_yamls:
        configs += y
    configs.parse()
    return configs


def do_work(parser, args=None, debug=False):
    """
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    global arg_options, arg_others, arg_rest
    arg_options, arg_others, arg_rest = parser.parse(args)
    Paths.format = PathFormat.ABSOLUTE
    if arg_options.root:
        Paths.base_dir(arg_options.root)

    # configure printer
    Printer.batch_output = arg_options.batch
    Printer.dynamic_output = not arg_options.batch

    # we need flow123d, mpiexec and ndiff to exists in LOCAL mode
    if not arg_options.queue and not Paths.test_paths('flow123d', 'mpiexec', 'ndiff'):
        Printer.err('Missing obligatory files! Exiting')
        GlobalResult.error = "missing obligatory files"
        sys.exit(1)

    # test yaml args
    if not arg_others:
        parser.exit_usage('Error: No yaml files or folder given')
        GlobalResult.error = "no yaml files or folder given"
        sys.exit(2)

    all_yamls = list()
    for path in arg_others:
        if not Paths.exists(path):
            Printer.err('Error! given path does not exists, ignoring path "{}"', path)
            GlobalResult.error = "path does not exist"
            sys.exit(3)

        if Paths.is_dir(path):
            all_yamls.extend(Paths.walk(path, filters=[
                PathFilters.filter_type_is_file(),
                PathFilters.filter_ext('.yaml'),
                PathFilters.filter_not(PathFilters.filter_name('config.yaml'))
            ]))
        else:
            all_yamls.append(path)

    Printer.out("Found {} .yaml file/s", len(all_yamls))
    if not all_yamls:
        Printer.wrn('Warning! No yaml files found in locations: \n  {}', '\n  '.join(arg_others))
        GlobalResult.error = "no yaml files or folders given"
        sys.exit(3)

    configs = read_configs(all_yamls)
    configs.update(
        proc=arg_options.cpu,
        time_limit=arg_options.time_limit,
        memory_limit=arg_options.memory_limit,
    )

    if arg_options.queue:
        Printer.out('Running in PBS mode')
        return run_pbs_mode(configs, debug)
    else:
        Printer.out('Running in LOCAL mode')
        return run_local_mode(configs, debug)
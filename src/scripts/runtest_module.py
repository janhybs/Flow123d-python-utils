#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import sys
from scripts.core import prescriptions
import progressbar as pb
from scripts.core.base import Paths, PathFormat, PathFilters, Printer, CommandEscapee, IO
from scripts.config.yaml_config import YamlConfig
from scripts.core.prescriptions import PBSModule
from scripts.execs.monitor import PyProcess
from scripts.execs.test_executor import BinExecutor, ParallelRunner, SequentialProcesses


# global arguments
from scripts.pbs.common import get_pbs_module

arg_options = None
arg_others = None
arg_rest = None
printer = Printer(Printer.LEVEL_KEY)


def create_process(command, limits=None):
    """
    :type command: list[str]
    :type limits: scripts.execs.monitor.Limits
    """
    test_executor = BinExecutor(command)
    process_monitor = PyProcess(test_executor)
    process_monitor.limit_monitor.set_limits(limits)
    return process_monitor


def create_process_from_case(case):
    """
    :type case: scripts.core.prescriptions.TestPrescription
    """
    process_monitor = create_process(case.get_command(), case.test_case)
    process_monitor.limit_monitor.active = False
    process_monitor.info_monitor.active = True
    process_monitor.info_monitor.end_fmt = ''
    process_monitor.info_monitor.start_fmt = 'Running: {} x {}'.format(
        case.proc_value,
        Paths.path_end(case.test_case.files[0])
        )

    # turn on output
    if arg_options.batch:
        process_monitor.progress_monitor.active = False
        process_monitor.info_monitor.stdout_stderr = None
    else:
        process_monitor.info_monitor.stdout_stderr = Paths.temp_file('run-test.log')

    seq = SequentialProcesses('test-case', pbar=False)
    seq.add(case.create_clean_thread())
    seq.add(process_monitor)

    # if clean-up fails do not run other
    seq.stop_on_error = True
    return seq


def create_pbs_job_content(module, command):
    escaped_command = ' '.join(CommandEscapee.escape_command(command))
    template = PBSModule.format(
        module.template,
        command=escaped_command,
        root=arg_options.root
    )

    return template


def create_pbs_command(qsub_command):
    return ' '.join(CommandEscapee.escape_command(qsub_command))


def run_pbs_mode(all_yamls):
    pbs_module = get_pbs_module(arg_options.host)

    total = len(all_yamls)
    yaml_i = 0

    jobs = list()
    for yaml_file in all_yamls:
        # parse config.yaml
        yaml_i += 1
        config = YamlConfig(yaml_file)

        # extract all test cases (product of cpu x files)
        for case in config.get_all_cases(pbs_module.Module):
            # create run command
            test_command = case.get_command()
            test_command.extend(arg_rest)
            pbs_content = create_pbs_job_content(pbs_module, test_command)
            IO.write(case.pbs_script, pbs_content)

            # create pbs file
            qsub_command = case.get_pbs_command(arg_options, case.pbs_script)
            jobs.append((create_pbs_command(qsub_command), case.pbs_script))


def run_local_mode(all_yamls):
    # create parallel runner instance
    runner = ParallelRunner(arg_options.parallel)

    for yaml_file, config in all_yamls.items():
        # extract all test cases (product of cpu x files)
        for case in config.get_all_cases(prescriptions.MPIPrescription, yaml_file):
            # create main process which first clean output dir
            # and then execute test
            print case
            continue
            multi_process = create_process_from_case(case)

            # get all comparisons threads and add them to main runner
            multi_process.add(case.create_comparison_threads())
            runner.add(multi_process)

    # now that we have everything prepared
    printer.dbg('Executing tasks')
    printer.key('-' * 60)
    runner.run()


def read_configs(all_yamls):
    all_configs = list(set([Paths.rename(y, 'config.yaml') for y in all_yamls]))
    all_configs = {c: YamlConfig(c) for c in all_configs}
    configs = {y: all_configs[Paths.rename(y, 'config.yaml')] for y in set(all_yamls)}
    for k, v in configs.items():
        v.include = arg_options.include
        v.exclude = arg_options.exclude
        # load all configs a then limit single config instances while traversing
        v.parse()

    return configs


def do_work(parser):
    """
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    global arg_options, arg_others, arg_rest
    arg_options, arg_others, arg_rest = parser.parse()
    Paths.format = PathFormat.ABSOLUTE

    # we need flow123d, mpiexec and ndiff to exists
    if not Paths.test_paths('flow123d', 'mpiexec', 'ndiff'):
        printer.err('Some files are not accessible! Exiting')
        printer.dbg('Make sure correct --root is specified')
        exit(1)

    # test yaml args
    if not arg_others:
        parser.exit_usage('Error: No yaml files or folder given')
        exit(1)

    all_yamls = list()
    for path in arg_others:
        if not Paths.exists(path):
            printer.wrn('Warning! given path does not exists, ignoring path "{}"', path)
            continue

        if Paths.is_dir(path):
            all_yamls.extend(Paths.walk(path, filters=[
                PathFilters.filter_type_is_file(),
                PathFilters.filter_ext('.yaml'),
                PathFilters.filter_not(PathFilters.filter_name('config.yaml'))
            ]))
        else:
            all_yamls.append(path)

    printer.key("Found {} .yaml solve file/s", len(all_yamls))
    if not all_yamls:
        printer.wrn('Warning! No yaml files found in locations: \n  {}', '\n  '.join(arg_others))
        exit(1)

    all_configs = read_configs(all_yamls)

    if arg_options.queue:
        printer.dbg('Running in PBS mode')
        printer.key('-' * 60)
        run_pbs_mode(all_configs)
    else:
        printer.dbg('Running in LOCAL mode')
        printer.key('-' * 60)
        run_local_mode(all_configs)
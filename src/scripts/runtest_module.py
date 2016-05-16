#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import sys
from scripts.core import prescriptions
import progressbar as pb
from scripts.core.base import Paths, PathFormat, PathFilters, Printer, CommandEscapee, IO
from scripts.config.yaml_config import YamlConfig
from scripts.core.prescriptions import PBSModule
from scripts.execs.monitor import ProcessMonitor
from scripts.execs.test_executor import BinExecutor, ParallelRunner, SequentialProcesses


# global arguments
from scripts.pbs.common import get_pbs_module

arg_options = None
arg_others = None
arg_rest = None


def create_process(command, limits=None):
    """
    :type command: list[str]
    :type limits: scripts.execs.monitor.Limits
    """
    test_executor = BinExecutor(command)
    process_monitor = ProcessMonitor(test_executor)
    process_monitor.limit_monitor.set_limits(limits)
    return process_monitor


def create_process_from_case(case):
    """
    :type case: scripts.execs.test_executor.TestPrescription
    """
    process_monitor = create_process(case.get_command(), case.test_case)

    seq = SequentialProcesses(False)
    seq.add(case.create_clean_thread())
    seq.add(process_monitor)
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
    pbar = pb.ProgressBar(maxval=total, term_width=60, fd=sys.stdout, widgets=['Preparing tasks ', pb.Bar('x')])
    pbar.start()
    yaml_i = 0

    jobs = list()
    for yaml_file in all_yamls:
        # parse config.yaml
        yaml_i += 1
        pbar.update(yaml_i)
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
    print jobs[3]


def run_local_mode(all_yamls):
    # create parallel runner instance
    runner = ParallelRunner(arg_options.parallel)

    total = len(all_yamls)
    pbar = pb.ProgressBar(maxval=total, term_width=60, fd=sys.stdout, widgets=['Preparing tasks ', pb.Bar('x')])
    pbar.start()
    yaml_i = 0
    for yaml_file in all_yamls:
        # parse config.yaml
        yaml_i += 1
        pbar.update(yaml_i)
        config = YamlConfig(yaml_file)

        # extract all test cases (product of cpu x files)
        for case in config.get_all_cases(prescriptions.MPIPrescription):
            # create main process which first clean output dir
            # and then execute test
            multi_process = SequentialProcesses(False)
            multi_process.add(create_process_from_case(case))
            multi_process.stop_on_error = True

            # get all comparisons threads and add them to main runner
            multi_process.add(case.create_comparison_threads())
            runner.add(multi_process)
    pbar.finish()

    # now that we have everything prepared
    Printer.out('Executing tasks')
    Printer.out('-' * 60)
    runner.run()


def do_work(frontend_file, parser):
    """
    :type frontend_file: str
    :type parser: utils.argparser.ArgParser
    """

    # parse arguments
    global arg_options, arg_others, arg_rest
    arg_options, arg_others, arg_rest = parser.parse()
    Paths.format = PathFormat.ABSOLUTE

    if not arg_options.root:
        # try to find our root
        arg_options.root = Paths.join(Paths.dirname(frontend_file), '..', '..')
        Printer.out('Argument --root not specified, assuming root is {}', arg_options.root)

    # make root absolute
    arg_options.root = Paths.abspath(arg_options.root)
    # change dir to root
    Paths.base_dir(arg_options.root)

    # we need flow123d, mpiexec and ndiff to exists
    if not Paths.test_paths('flow123d', 'mpiexec', 'ndiff'):
        Printer.err('Some files are not accessible! Exiting')
        Printer.err('Make sure correct --root is specified')
        exit(1)

    # test yaml args
    if not arg_others:
        parser.exit_usage('Error: No yaml files or folder given', arg_options.root)
        exit(1)

    all_yamls = list()
    for path in arg_others:
        if not Paths.exists(path):
            Printer.err('Warning! given path does not exists, ignoring path "{}"', path)
            continue

        if Paths.is_dir(path):
            all_yamls.extend(Paths.walk(path, filters=[
                PathFilters.filter_type_is_file(),
                PathFilters.filter_name('config.yaml')
            ]))
        else:
            all_yamls.append(path)

    Printer.out("Found {} config.yaml file/s", len(all_yamls))
    if not all_yamls:
        Printer.err('Warning! No yaml files found in locations: \n  {}', '\n  '.join(arg_others))
        exit(1)

    if arg_options.queue:
        Printer.out('Running in PBS mode')
        run_pbs_mode(all_yamls)
    else:
        Printer.out('Running in LOCAL mode')
        run_local_mode(all_yamls)
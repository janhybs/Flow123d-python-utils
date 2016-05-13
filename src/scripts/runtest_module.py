#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import sys
from scripts.core import prescriptions
import progressbar as pb
from scripts.core.base import Paths, PathFormat, PathFilters, Printer, CommandEscapee, IO
from scripts.config.yaml_config import YamlConfig
from scripts.execs.monitor import ProcessMonitor
from scripts.execs.test_executor import BinExecutor, ParallelRunner, SequentialProcesses
from utils.argparser import ArgParser


usage = "runtest.py [<parametes>] [<test set>]  [-- <test arguments>]"

parser = ArgParser(usage)
# ----------------------------------------------
parser.add_section('General arguments')
parser.add('-a', '--keep-going', type=True, name='keep_going', docs=[
    'Run all tests, do not stop on the first error.',
    'In PBS mode this arguments is ignored.',
])
parser.add('-p', '--parallel', type=int, name='parallel', default=1, placeholder='<N>', docs=[
    'Run at most N tests in parallel.',
    'In PBS mode this arguments is ignored.',
])
parser.add('-v', '', type=True, name='valgrind_on', docs=[
    'Run tests under valgrind, with python suppression.',
    '(In PBS mode this arguments is ignored.)',
])
parser.add('', '--valgrind', type=str, name='valgrind_args', placeholder='<VALGRIND ARGS>', docs=[
    'Same as previous option, but  pass arguments <valgrind args>',
    'to the valgrind. (In PBS mode this arguments is ignored.)',
])
# ----------------------------------------------
parser.add_section('Passable arguments to run_parallel.py')
parser.add('-n', '--cpu', type=list, subtype=int, name='cpu', placeholder='<proc set>', docs=[
    'Run for every number of processes in the <proc set>',
    '  The <proc set> can be set as:',
    '     - single number (can be defined multiple times)',
    '     - set             "[1,3,4]" or [1 2 4]',
    '     - range           "1:4"   = "[1,2,3,4]"',
    '     - range with step "1:7:2" = "[1,3,5,7]"',
])
parser.add('-q', '--queue', type=[True, str], name='queue', placeholder='[<queue>]', docs=[
    'Optional PBS queue name to use. If the parameter is not used, ',
    'the application is executed in the same process and without PBS.',
    '',
    'If used without <queue> argument it is executed in the ',
    'background preferably under PBS with the queue selected ',
    'automatically for the given wall clock time limit and number of processes.'
])
parser.add('', '--host', type=str, name='host', placeholder='<host>', docs=[
    'Name of the running host that is used to select system ',
    'specific setup script. Default value of this parameter ',
    'is obtained by first getting the hostname ',
    '(using platform.node() or socket.gethostname()) and then search',
    'it in the table "host_table.json" which assign logical hostname',
    'possibly to multiple different real hostnames. ',
    '',
    'If the real host name is not found in the table ',
    'it is used directly otherwise the logical ',
    'hostname is used to select the setup script.',
])
# ----------------------------------------------
parser.add_section('Passable arguments to exec_with_limit.py')
parser.add('-t', '--limit-time', type=float, name='time_limit', placeholder='<time>', docs=[
    'Obligatory wall clock time limit for execution in seconds',
    'For precision use float value'
])
parser.add('-m', '--limit-memory', type=float, name='memory_limit', placeholder='<memory>', docs=[
    'Optional memory limit per node in MB',
    'For precision use float value'
])
# ----------------------------------------------
parser.add_section('Proposed arguments')
parser.add('', '--root', type=str, name='root', placeholder='<root>', docs=[
    'Optional hint for flow123d path, if not specified, default value will be',
    'Extracted from this file path, assuming it is located in flow123d bin/python dir',
    '',
    'Script will always change-dir itself to location of root, so all path match'
])
# ----------------------------------------------


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
    return module.template.replace('$$command$$',escaped_command)


def create_pbs_command(qsub_command):
    return ' '.join(CommandEscapee.escape_command(qsub_command))


def run_pbs_mode(all_yamls, options, rest):
    import platform, json, importlib

    hostname = platform.node()

    with open('host_table.json', 'r') as fp:
        hosts = json.load(fp)
        pbs_module_path = hosts.get(hostname)


    total = len(all_yamls)
    pbar = pb.ProgressBar(maxval=total, term_width=60, fd=sys.stdout, widgets=['Preparing tasks ', pb.Bar('x')])
    pbar.start()
    yaml_i = 0

    pbs_module = importlib.import_module('scripts.pbs.modules.{}'.format(pbs_module_path))
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
            test_command.extend(rest)
            pbs_content = create_pbs_job_content(pbs_module, test_command)
            IO.write(case.pbs_script, pbs_content)

            # create pbs file
            qsub_command = case.get_pbs_command(options, case.pbs_script)
            jobs.append((create_pbs_command(qsub_command), case.pbs_script))


def run_local_mode(all_yamls, options, rest):
    # create parallel runner instance
    runner = ParallelRunner(options.parallel)

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


def do_work(frontend_file):
    # parse arguments
    options, yamls, rest = parser.parse()
    Paths.format = PathFormat.ABSOLUTE

    if not options.root:
        # try to find our root
        options.root = Paths.join(Paths.dirname(frontend_file), '..', '..')
        Printer.out('Argument --root not specified, assuming root is {}', options.root)

    # change dir to root
    Paths.base_dir(options.root)
    if not Paths.exists(Paths.flow123d()):
        Printer.err('Error: Invalid root! Could not find binary files relative to root {}', options.root)
        Printer.err('Error: Flow123d binary file not found in {}', Paths.flow123d())
        exit(1)

    # test yaml args
    if not yamls:
        Printer.err('Error: No yaml files or folder given', options.root)
        exit(1)

    all_yamls = list()
    for path in yamls:
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
        Printer.err('Warning! No yaml files found in locations: \n  {}', '\n  '.join(yamls))
        exit(1)

    if options.queue:
        Printer.out('Running in PBS mode')
        run_pbs_mode(all_yamls, options, rest)
    else:
        Printer.out('Running in LOCAL mode')
        run_local_mode(all_yamls, options, rest)
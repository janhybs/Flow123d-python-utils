#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from __future__ import absolute_import
import sys; sys.path.append('.')

import progressbar as pb
from scripts.core.base import Paths, PathFormat, PathFilters, Printer
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
        for case in config.get_all_cases():
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


def do_work():
    # parse arguments
    options, yamls, rest = parser.parse()

    all_yamls = list()
    for path in yamls:
        if Paths.is_dir(path):
            all_yamls.extend(Paths.walk(path, filters=[
                PathFilters.filter_type_is_file(),
                PathFilters.filter_name('config.yaml')
            ]))
        else:
            all_yamls.append(path)

    Printer.out("Found {} config.yaml file/s", len(all_yamls))
    if options.queue:
        Printer.out('Running in PBS mode')
        # run_pbs(all_yamls)
    else:
        Printer.out('Running in LOCAL mode')
        run_local_mode(all_yamls, options, rest)


Paths.base_dir('/home/jan-hybs/Dokumenty/Smartgit-flow/flow123d/')
Paths.format = PathFormat.RELATIVE
# path = Paths.path_to('tests', '03_transport_small_12d', 'config.yaml')
# cfg = YamlConfig(path)
#
# runner = ParallelRunner(1)
#
# for case in cfg.get_all_cases():
#     # create seq thread for single case and add main execution
#     multi_process = SequentialProcesses(False)
#     multi_process.add(create_process_from_case(case))
#     multi_process.stop_on_error = True
#
#     # get all comparisons
#     pairs = case.get_ref_output_ndiff_files()
#     compares = SequentialProcesses()
#     compares.thread_name_property = True
#     compares.name = "File compare"
#     for pair in pairs:
#         pm = ProcessMonitor(
#             BinExecutor([
#                 Paths.ndiff(),
#                 Paths.abspath(pair[0]),
#                 Paths.abspath(pair[1])
#             ]))
#         pm.name = '{} {}'.format(Paths.basename(pair[0]), Paths.filesize(pair[0], True))
#         pm.info_monitor.stdout_stderr = case.ndiff_log
#         compares.add(pm)
#
#     # add all comparisons to main thread
#     multi_process.add(compares)
#     runner.add(multi_process)
# runner.run()

# create_process('Calculator.exe', Limits(5, 3)).start()
# create_process('calc', Limits(5, 3)).start()

do_work()
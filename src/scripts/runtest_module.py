#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from scripts.core.base import Paths, PathFormat
from scripts.config.yaml_config import YamlConfig
from scripts.execs.monitor import ProcessMonitor, LimitMonitor, Limits
from scripts.execs.test_executor import BinExecutor, ParallelRunner, MultiProcess
from utils.argparser import ArgParser

usage = "runtest.py [<parametes>] [<test set>]  [-- <test arguments>]"

parser = ArgParser(usage)
# ----------------------------------------------
parser.add_section('General arguments')
parser.add('-a', '--keep-going', type=True, name='keep_going', docs=[
    'Run all tests, do not stop on the first error.',
    'In PBS mode this arguments is ignored.',
])
parser.add('-p', '--parallel', type=int, name='parallel', placeholder='<N>', docs=[
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
    test_executor = BinExecutor(command)
    process_monitor = ProcessMonitor(test_executor)
    process_monitor.limit_monitor.set_limits(limits)
    return process_monitor


def create_process_from_case(case):
    """
    :type case: scripts.execs.test_executor.TestPrescription
    """
    return create_process(case.get_command(), case.test_case)

# Paths.base_dir('/home/jan-hybs/Dokumenty/Smartgit-flow/flow123d/')
# Paths.format = PathFormat.RELATIVE
# path = Paths.path_to('tests', '03_transport_small_12d', 'config.yaml')
# cfg = YamlConfig(path)

# runner = ParallelRunner(1)
#
# for case in cfg.get_all_cases():
#     process_monitor = create_process_from_case(case)
#     runner.add(
#         MultiProcess(
#             process_monitor
#         )
#     )
# runner.run()

# create_process('Calculator.exe', Limits(5, 3)).start()
# create_process('calc', Limits(5, 3)).start()

import psutil
# print psutil.Process(8676)
# print psutil.Process(7184).ppid()
#
# Název	PID	Stav	Uživatelské jméno	Procesor	Paměť (soukromá pracovní sada)	Příkazový řádek	Popis
# Calculator.exe	5432	Spuštěno	x3mSpeedy	00 	14 100 k	"C:\Program Files\WindowsApps\Microsoft.WindowsCalculator_10.1601.49020.0_x64__8wekyb3d8bbwe\Calculator.exe" -ServerName:App.AppXsm3pg4n7er43kdh1qp4e79f1j7am68r8.mca	Calculator.exe

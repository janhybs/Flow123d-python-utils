#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
from subprocess import PIPE
from scripts.base import Paths, PathFormat
from scripts.config.yaml_config import YamlConfig
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
parser.add('-t', '--limit-time', type=float, name='limit_time', placeholder='<time>', docs=[
    'Obligatory wall clock time limit for execution in seconds',
    'For precision use float value'
])
parser.add('-m', '--limit-memory', type=float, name='limit_memory', placeholder='<memory>', docs=[
    'Optional memory limit per node in MB',
    'For precision use float value'
])

# print parser.usage()
# opts = parser.parse(['-a', '-n', '0:50:10'])[0]
# print opts.get('cpu').value
# print opts.get('queue').value
#
# class Foo(object):
#     def __init__(self):
#         self.bar = 5
#
#
#     def run(self):
#         return ['foo', self.bar]
#
#
#
# def my_run(self):
#     return [self.bar]
#
# Foo.run = my_run()
#
#
#
# print Foo()

# import psutil
#
# Paths.base_dir('/home/jan-hybs/Dokumenty/Smartgit-flow/flow123d/')
# Paths.format = PathFormat.RELATIVE
# path = Paths.path_to('tests', '03_transport_small_12d', 'config.yaml')
# cfg = YamlConfig(path)
# for executor in cfg.get_all_executions():
#     command = executor.get_command()
#     popen = psutil.Popen(command, stderr=PIPE, stdout=PIPE)
#     popen.wait()
#     print popen.returncode


import time
from progressbar import ProgressBar, Counter, Timer, AnimatedMarker, Bar, Percentage
widgets = ['Running  ', AnimatedMarker(), ' ', Timer(), ')', Bar(), Percentage()]
p = ProgressBar(widgets=widgets, maxval=100)
p.start()
for i in range(100):
    p.update(i)
    time.sleep(0.01)
p.finish()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# import sys
# import time
#
# from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
#      FileTransferSpeed, FormatLabel, Percentage, \
#     ProgressBar, ReverseBar, RotatingMarker, \
#     SimpleProgress, Timer
#
# examples = []
# def example(fn):
#     try: name = 'Example %d' % int(fn.__name__[7:])
#     except: name = fn.__name__
#
#     def wrapped():
#         try:
#             sys.stdout.write('Running: %s\n' % name)
#             fn()
#             sys.stdout.write('\n')
#         except KeyboardInterrupt:
#             sys.stdout.write('\nSkipping example.\n\n')
#
#     examples.append(wrapped)
#     return wrapped
#
# @example
# def example0():
#     pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=300).start()
#     for i in range(300):
#         time.sleep(0.01)
#         pbar.update(i+1)
#     pbar.finish()
#
# @example
# def example1():
#     widgets = ['Test: ', Percentage(), ' ', Bar(marker=RotatingMarker()),
#                ' ', ETA(), ' ', FileTransferSpeed()]
#     pbar = ProgressBar(widgets=widgets, maxval=10000000).start()
#     for i in range(1000000):
#         # do something
#         pbar.update(10*i+1)
#     pbar.finish()
#
# @example
# def example2():
#     class CrazyFileTransferSpeed(FileTransferSpeed):
#         """It's bigger between 45 and 80 percent."""
#         def update(self, pbar):
#             if 45 < pbar.percentage() < 80:
#                 return 'Bigger Now ' + FileTransferSpeed.update(self,pbar)
#             else:
#                 return FileTransferSpeed.update(self,pbar)
#
#     widgets = [CrazyFileTransferSpeed(),' <<<', Bar(), '>>> ',
#                Percentage(),' ', ETA()]
#     pbar = ProgressBar(widgets=widgets, maxval=10000000)
#     # maybe do something
#     pbar.start()
#     for i in range(2000000):
#         # do something
#         pbar.update(5*i+1)
#     pbar.finish()
#
# @example
# def example3():
#     widgets = [Bar('>'), ' ', ETA(), ' ', ReverseBar('<')]
#     pbar = ProgressBar(widgets=widgets, maxval=10000000).start()
#     for i in range(1000000):
#         # do something
#         pbar.update(10*i+1)
#     pbar.finish()
#
# @example
# def example4():
#     widgets = ['Test: ', Percentage(), ' ',
#                Bar(marker='0',left='[',right=']'),
#                ' ', ETA(), ' ', FileTransferSpeed()]
#     pbar = ProgressBar(widgets=widgets, maxval=500)
#     pbar.start()
#     for i in range(100,500+1,50):
#         time.sleep(0.2)
#         pbar.update(i)
#     pbar.finish()
#
# @example
# def example5():
#     pbar = ProgressBar(widgets=[SimpleProgress()], maxval=17).start()
#     for i in range(17):
#         time.sleep(0.2)
#         pbar.update(i + 1)
#     pbar.finish()
#
# @example
# def example6():
#     pbar = ProgressBar().start()
#     for i in range(100):
#         time.sleep(0.01)
#         pbar.update(i + 1)
#     pbar.finish()
#
# @example
# def example7():
#     pbar = ProgressBar()  # Progressbar can guess maxval automatically.
#     for i in pbar(range(80)):
#         time.sleep(0.01)
#
# @example
# def example8():
#     pbar = ProgressBar(maxval=80)  # Progressbar can't guess maxval.
#     for i in pbar((i for i in range(80))):
#         time.sleep(0.01)
#
# @example
# def example9():
#     pbar = ProgressBar(widgets=['Working: ', AnimatedMarker()])
#     for i in pbar((i for i in range(50))):
#         time.sleep(.08)
#
# @example
# def example10():
#     widgets = ['Processed: ', Counter(), ' lines (', Timer(), ')']
#     pbar = ProgressBar(widgets=widgets)
#     for i in pbar((i for i in range(150))):
#         time.sleep(0.1)
#
# @example
# def example11():
#     widgets = [FormatLabel('Processed: %(value)d lines (in: %(elapsed)s)')]
#     pbar = ProgressBar(widgets=widgets)
#     for i in pbar((i for i in range(150))):
#         time.sleep(0.1)
#
# @example
# def example12():
#     widgets = ['Balloon: ', AnimatedMarker(markers='.oO@* ')]
#     pbar = ProgressBar(widgets=widgets)
#     for i in pbar((i for i in range(24))):
#         time.sleep(0.3)
#
# @example
# def example13():
#     # You may need python 3.x to see this correctly
#     try:
#         widgets = ['Arrows: ', AnimatedMarker(markers='←↖↑↗→↘↓↙')]
#         pbar = ProgressBar(widgets=widgets)
#         for i in pbar((i for i in range(24))):
#             time.sleep(0.3)
#     except UnicodeError: sys.stdout.write('Unicode error: skipping example')
#
# @example
# def example14():
#     # You may need python 3.x to see this correctly
#     try:
#         widgets = ['Arrows: ', AnimatedMarker(markers='◢◣◤◥')]
#         pbar = ProgressBar(widgets=widgets)
#         for i in pbar((i for i in range(24))):
#             time.sleep(0.3)
#     except UnicodeError: sys.stdout.write('Unicode error: skipping example')
#
# @example
# def example15():
#     # You may need python 3.x to see this correctly
#     try:
#         widgets = ['Wheels: ', AnimatedMarker(markers='◐◓◑◒')]
#         pbar = ProgressBar(widgets=widgets)
#         for i in pbar((i for i in range(24))):
#             time.sleep(0.3)
#     except UnicodeError: sys.stdout.write('Unicode error: skipping example')
#
# @example
# def example16():
#     widgets = [FormatLabel('Bouncer: value %(value)d - '), BouncingBar()]
#     pbar = ProgressBar(widgets=widgets)
#     for i in pbar((i for i in range(180))):
#         time.sleep(0.05)
#
# @example
# def example17():
#     widgets = [FormatLabel('Animated Bouncer: value %(value)d - '),
#                BouncingBar(marker=RotatingMarker())]
#
#     pbar = ProgressBar(widgets=widgets)
#     for i in pbar((i for i in range(180))):
#         time.sleep(0.05)
#
#
# @example
# def example19():
#   pbar = ProgressBar()
#   for i in pbar([]):
#     pass
#   pbar.finish()
#
# if __name__ == '__main__':
#     try:
#         for example in examples: example()
#     except KeyboardInterrupt:
#         sys.stdout.write('\nQuitting examples.\n')
#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
# ----------------------------------------------
import os
import sys
# ----------------------------------------------
import scripts as scripts_init
from unittest import TestCase
from exec_parallel import parser
from scripts.core.base import IO
from scripts.exec_parallel_module import do_work
# ----------------------------------------------

consumer = os.path.join(os.path.dirname(scripts_init.__file__), 'c++', 'main')
root = r'/home/jan-hybs/Dokumenty/projects/Flow123d/flow123d'
__dir__ = os.path.dirname(os.path.realpath(__file__))


def print_test(f):
    def wrapper(*args, **kwargs):
        sys.stdout.write('#' * 60 + '\n')
        sys.stdout.write('  EXECUTING {:^48s}'.format(f.func_name) + '\n')
        sys.stdout.write('-' * 60 + '\n')
        # try:
        f(*args, **kwargs)
        #     sys.stdout.write('-' * 60 + '\n')
        #     sys.stdout.write('  SUCCESS {:^48s}'.format(f.func_name) + '\n')
        #     sys.stdout.write('\n\n')
        # except Exception as e:
        #     sys.stdout.write('-' * 60 + '\n')
        #     sys.stdout.write('  FAILED {:^48s}'.format(f.func_name) + '\n')
        #     sys.stdout.write('\n\n')
        #     raise e
    return wrapper


class TestDoWork(TestCase):

    @print_test
    def test_help(self):
        try:
            do_work(parser, ['--help'])
            self.fail()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @print_test
    def test_empty(self):
        try:
            do_work(parser, [])
            self.fail()
            pass
        except SystemExit as e:
            self.assertEqual(e.code, 1)

    @print_test
    def test_no_limits(self):
        returncode = do_work(parser, ['--root', root, '--', 'mpirun', 'sleep', '0.1'])
        self.assertEqual(returncode, 0)

    @print_test
    def test_time_limit_ok(self):
        returncode = do_work(parser, ['-t', '1', '--root', root, '--', 'mpirun', 'sleep', '0.1'])
        self.assertEqual(returncode, 0)

        np = '2'
        pypy = do_work(parser, ['-n', np, '-t', '1', '--root', root, '--', 'mpirun', 'sleep', '0.1'], debug=True)
        self.assertEqual(pypy.returncode, 0)
        self.assertEqual(int(pypy.executor.command[2]), int(np))

    @print_test
    def test_time_limit_over(self):
        returncode = do_work(parser, ['-t', '0.1', '--root', root, '--', 'mpirun', 'sleep', '2'])
        self.assertNotEqual(returncode, 0)

        np = '2'
        pypy = do_work(parser, ['-n', np, '-t', '0.1', '--root', root, '--', 'mpirun', 'sleep', '2'], debug=True)
        self.assertNotEqual(pypy.returncode, 0)
        self.assertEqual(int(pypy.executor.command[2]), int(np))

    @print_test
    def test_memory_limit_ok(self):
        returncode = do_work(parser, ['-n', '1', '-m', '100', '--root', root, '--', 'mpirun', consumer, '-m', '10', '-t', '1'])
        self.assertEqual(returncode, 0)

        returncode = do_work(parser, ['-n', '2', '-m', '200', '--root', root, '--', 'mpirun', consumer, '-m', '10', '-t', '1'])
        self.assertEqual(returncode, 0)

        np = '2'
        pypy = do_work(parser, ['-n', np, '-m', '200', '--root', root, '--', 'mpirun', consumer, '-m', '10', '-t', '1'], debug=True)
        self.assertEqual(int(pypy.returncode), 0)
        self.assertEqual(int(pypy.executor.command[2]), int(np))

    @print_test
    def test_memory_limit_over(self):
        returncode = do_work(parser, ['-n', '1', '-m', '100', '--root', root, '--', 'mpirun', consumer, '-m', '200', '-t', '5'])
        self.assertNotEqual(returncode, 0)

        returncode = do_work(parser, ['-n', '2', '-m', '200', '--root', root, '--', 'mpirun', consumer, '-m', '200', '-t', '1'])
        self.assertNotEqual(returncode, 0)

        np = '2'
        pypy = do_work(parser, ['-n', np, '-m', '200', '--root', root, '--', 'mpirun', consumer, '-m', '200', '-t', '1'], debug=True)
        self.assertNotEqual(int(pypy.returncode), 0)
        self.assertEqual(int(pypy.executor.command[2]), int(np))

    @print_test
    def test_pbs_mode(self):
        # this test can be only tested on PBS server

        do_work(parser, ['-q', '--', 'sleep', '1'], debug=True)
        mpi_dirs = [f for f in os.listdir(__dir__) if f.startswith('exec-parallel-')]
        self.assertGreaterEqual(len(mpi_dirs), 1)

        # test that script were actually created and contain at least one file
        # also remove them ...
        for mpi in mpi_dirs:
            self.assertGreaterEqual(len(os.listdir(os.path.join(__dir__, mpi))), 1)
            IO.delete_all(os.path.join(__dir__, mpi))

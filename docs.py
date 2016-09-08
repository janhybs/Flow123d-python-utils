#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import os
import re
from subprocess import check_output

__dir__ = os.path.dirname(os.path.realpath(__file__))
def_regex = re.compile(r'(def|class) ([a-zA-Z_0-9]+)')
doc_regex = re.compile(r'"""|\'\'\'')

os.chdir(__dir__)
src = os.path.join('src')
tests = os.path.join('tests')

src_files = check_output(['find', src, '-type', 'f', '-name', '*.py']).splitlines()
tests_files = check_output(['find', tests, '-type', 'f', '-name', '*.py']).splitlines()


def check_docs(files, types=('def', 'class')):
    result = dict()
    for f in files:
        with open(f, 'r') as fp:
            c = fp.read().splitlines()
            for i in range(len(c)-2):
                curr = c[i]
                next = c[i+1]
                futu = c[i+2]

                match = def_regex.findall(curr)
                if match and curr.find(':') != -1:
                    type_allowed = False
                    for t in types:
                        if curr.startswith(t):
                            type_allowed = True
                    if not type_allowed:
                        continue

                    if not doc_regex.findall(next) or futu.strip().startswith(':'):
                        if f not in result:
                            result[f] = list()
                        result[f].append('{i:<3} : {match[0][1]:30s} {match[0][0]:>20s}'.format(**locals()))

    keys = sorted(result.keys())

    for r in keys:
        v = result[r]
        print('{r}'.format(**locals()))
        for l in v:
            print('{:30s}{l:s}'.format('', **locals()))
        print('')


check_docs(src_files, types=['class', 'def'])
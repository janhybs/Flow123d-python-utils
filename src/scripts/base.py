#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import sys, os


def make_relative(f):
    def wrapper(*args, **kwargs):
        path = f(*args, **kwargs)
        if Paths.format == PathFormat.RELATIVE:
            return os.path.relpath(path, Paths.base_dir())
        elif Paths.format == PathFormat.ABSOLUTE:
            return os.path.abspath(path)
        return path
    return wrapper


class PathFilters(object):
    @staticmethod
    def filter_name(name):
        return lambda x: Paths.basename(x) == name

    @staticmethod
    def filter_ext(ext):
        return lambda x: Paths.basename(x).endswith(ext)

    @staticmethod
    def filter_not(f):
        return lambda x: not f(x)

    @staticmethod
    def filter_type_is_file():
        def f(path):
            return os.path.isfile(path)
        return f #lambda x: os.path.isfile(x)

    @staticmethod
    def filter_type_is_dir():
        return lambda x: os.path.isdir(x)

    @staticmethod
    def filter_exists():
        return lambda x: os.path


class PathFormat(object):
    CUSTOM = 0
    RELATIVE = 1
    ABSOLUTE = 2


class Paths(object):
    _base_dir = './'
    format = PathFormat.ABSOLUTE

    @classmethod
    def base_dir(cls, v=None):
        if v is None:
            return cls._base_dir
        else:
            cls._base_dir = v
            os.chdir(v)

    # -----------------------------------

    @classmethod
    @make_relative
    def ndiff(cls):
        return cls.path_to('bin', 'ndiff', 'ndiff.pl')

    @classmethod
    @make_relative
    def flow123d(cls):
        return cls.path_to('bin', 'flow123d')

    @classmethod
    @make_relative
    def mpiexec(cls):
        return cls.path_to('bin', 'mpiexec')

    # -----------------------------------

    @classmethod
    @make_relative
    def path_to(cls, *args):
        return os.path.join(cls.base_dir(), *args)

    @classmethod
    @make_relative
    def join(cls, path, *paths):
        return os.path.join(path, *paths)

    @classmethod
    def basename(cls, path):
        return os.path.basename(path)

    @classmethod
    @make_relative
    def dirname(cls, path):
        return os.path.dirname(path)

    @classmethod
    @make_relative
    def without_ext(cls, path):
        return os.path.splitext(path)[0]

    @classmethod
    def browse(cls, path, filters=()):
        paths = [cls.join(path, p) for p in os.listdir(path)]
        for f in filters:
            paths = [p for p in paths if f(p)]
        return paths
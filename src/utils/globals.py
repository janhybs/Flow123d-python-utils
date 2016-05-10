#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs


def ensure_iterable(o):
    """
    Method ensure that given object is iterable(list or tuple)
    :param o: tested object
    :return: list or tuple
    """
    return [o] if type(o) not in (list, tuple) else o


def apply_to_all(lst, mtd, *args, **kwargs):
    """
    Method will call mtd on every object in lst
    :param lst: list of objects
    :param mtd: string name of callable method
    :param args:
    :param kwargs:
    """
    for x in lst:
        getattr(x, mtd)(*args, **kwargs)
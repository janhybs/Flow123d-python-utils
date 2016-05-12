#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs
import time, os


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


def wait_for(obj, property, period=0.1, max_wait=5):
    """
    Method will wait until property prop on object o exists
    and is not None
    Careful use since if value exists and value is None, can cause thread block
    :param obj:
    :param property:
    :param period:
    :param max_wait:
    :return:
    """
    wait = 0
    while True:
        attr = getattr(obj, property, None)
        if attr is not None:
            return attr

        time.sleep(period)
        wait += period
        if wait > max_wait:
            return None
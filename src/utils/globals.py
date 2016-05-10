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
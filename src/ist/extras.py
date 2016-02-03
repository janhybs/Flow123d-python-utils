#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from ist.globals import Globals
from ist.base import Parsable, Field


class TypeReference(Parsable):
    """
    :type reference  : unicode
    """
    __fields__ = [
    ]

    def parse(self, json_data={ }):
        self.reference = json_data
        return self

    def __init__(self):
        self.reference = None

    def get_reference(self):
        """
        :rtype : ist.nodes.TypeRecord or ist.nodes.TypeSelection or ist.nodes.TypeAbstract
        or ist.nodes.TypeString or nodes.Integer or ist.nodes.TypeDouble or ist.nodes.TypeArray
        or ist.nodes.TypeParameter or ist.nodes.TypeFilename or ist.nodes.TypeBool
        """
        return Globals.items[self.reference]


class TypeSelectionValue(Parsable):
    """
    :type name           : unicode
    :type description    : unicode
    """
    __fields__ = [
        Field('name'),
        Field('description'),
    ]

    def __init__(self):
        self.name = None
        self.description = None


class TypeRecordKeyDefault(Parsable):
    """
    :type type           : unicode
    :type value          : unicode
    """
    __fields__ = [
        Field('type'),
        Field('value'),
    ]

    def __init__(self):
        self.type = None
        self.value = None


class TypeRecordKey(Parsable):
    """
    :type key            : unicode
    :type type           : ist.extras.TypeReference
    :type default        : ist.extras.TypeRecordKeyDefault
    :type description    : unicode
    """
    __fields__ = [
        Field('key'),
        Field('type', t=TypeReference),
        Field('default', t=TypeRecordKeyDefault),
        Field('description'),
    ]

    def __init__(self):
        self.key = None
        self.type = None
        self.default = None
        self.description = None


class TypeRange(Parsable):
    __fields__ = []

    replacements = {
        '2147483647': 'INT32 MAX',
        '4294967295': 'UINT32 MAX',
        '-2147483647': 'INT32 MIN',
        '1.79769e+308': '+inf',
        '-1.79769e+308': '-inf',
        '': 'unknown range'
    }

    def parse(self, json_data={ }):
        self.min = json_data[0]
        self.max = json_data[0]
        return self

    def __init__(self):
        self.min = ''
        self.max = ''
        self.always_visible = True

    def is_pointless(self):
        """
         Whether is information within this instance beneficial
        """
        return self._format() in ('[0, ]', '[, ]', '(-inf, +inf)')

    def _format(self):
        """
        Method will will return string representation of this range
        :return:
        """
        min_value = self.replacements.get(str(self.min), str(self.min))
        max_value = self.replacements.get(str(self.max), str(self.max))
        l_brace = '(' if min_value.find('inf') != -1 else '['
        r_brace = ')' if max_value.find('inf') != -1 else ']'

        return '{l_brace}{min_value}, {max_value}{r_brace}'.format(
            l_brace=l_brace, r_brace=r_brace,
            min_value=min_value, max_value=max_value)

    def __repr__(self):
        """
        method will return string representation if is meaningful or flag always visible
        is True
        """
        return self._format() if self.always_visible or not self.is_pointless() else ''
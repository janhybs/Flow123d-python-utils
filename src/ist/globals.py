# encoding: utf-8
# author:   Jan Hybs

from __future__ import absolute_import
from utils.logger import Logger


class Globals(object):
    """
    Global class object which stores references and all objects on memory for later use
    :type items             : dict[ist.base.Parsable]
    """
    items = { }
    names = {
        'record': 'type_name',
        'r': 'type_name',
        'abstractrecord': 'name',
        'a': 'name',
        'ar': 'name',
        'selection': 'name',
        's': 'name',
        '': 'name'
    }

    @staticmethod
    def iterate():
        """
        :rtype : list[ist.base.Parsable]
        """
        return Globals.items.itervalues()

    @staticmethod
    def get_url_by_name(label, type=''):
        """
        constructs and returns tuple (name, type, link) from given name and label
        :param label: name#field where field is optional
        :param type:
        :rtype : list[ist.base.Parsable]
        """
        from ist.utils.htmltree import htmltree
        parts = label.split("#")
        name = parts[0]
        field = parts[1] if len(parts) > 1 else None

        for item in Globals.iterate():
            possibilities = item.gets('name', 'id', 'link_name')
            possibilities = [str(p).lower() for p in possibilities if p]

            if name.lower() in possibilities:
                # only link to item?
                if not field:
                    return item, None
                else:
                    return item, item.get_fields(field)

        return None, None, None

    @staticmethod
    def save(key, item):
        if key in Globals.items:
            Logger.instance().warning('duplicate key %s' % key)
            for i in range(2, 100):
                new_key = '{}-{}'.format(key, i)
                if new_key not in Globals.items:
                    Logger.instance().warning('For key %s assigned %s' % (key, new_key))
                    Globals.items[new_key] = item
                    return new_key
        Globals.items[key] = item
        return key
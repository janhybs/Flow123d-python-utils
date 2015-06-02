# encoding: utf-8
# author:   Jan Hybs


class Globals (object):
    items = {}
    names = {
        'record': 'type_name',
        'abstractrecord': 'name',
        'selection': 'name',
        '': 'name'
    }

    @staticmethod
    def get_by_name (name, type=''):
        for (id, item) in Globals.items.iteritems():
            try:
                if item.get(Globals.names.get(type.lower())).lower() == name.lower():
                    return item
            except:
                # no such attribute
                pass

        return None
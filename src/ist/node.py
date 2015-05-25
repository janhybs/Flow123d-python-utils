# encoding: utf-8
# author:   Jan Hybs


import json


class ISTNode (object):
    pass


class TypedList (list):
    def __init__ (self, cls=None, *args, **kwargs):
        self.cls = cls
        list.__init__ (self, *args, **kwargs)

    def parse (self, lst):
        if self.cls is None:
            for o in lst:
                if o.get ('input_type', '') == 'Record':
                    self.append (Record ().parse (o))
                if o.get ('input_type', '') == 'AbstractRecord':
                    self.append (AbstractRecord ().parse (o))
                else:
                    self.append (o)
        else:
            for o in lst:
                self.append (self.cls ().parse (o))
        return self


class Field (object):
    def __init__ (self, name, value=None, type=str):
        self.name = name
        self.value = value
        self.type = type if value is None else value.__class__

    def __repr__(self):
        return '<F {self.name}>'.format(self=self)


class AbstractNode (ISTNode):
    def __init__ (self):
        self._fields = []
        self._add_fields ([
            Field ('id'),
            Field ('input_type')
        ])

    def _add_fields (self, fields):
        self._fields.extend (fields)

    def parse (self, o={ }):
        for field in self._fields:
            # parse list
            if issubclass (field.type, TypedList):
                value = field.value.parse (o.get (field.name, []))
            # parse more complex objects
            elif issubclass (field.type, ISTNode):
                value = field.value.parse (o.get (field.name, { }))
            # simple values
            else:
                if type (o) is unicode:
                    print o
                value = o.get (field.name)

            # create attribute on class instance
            self.__setattr__ (field.name, value)
        return self


class DescriptionNode (AbstractNode):
    def __init__ (self):
        super (DescriptionNode, self).__init__ ()
        self._add_fields ([
            Field ('description')
        ])


class RecordKeyNode (AbstractNode):
    def __init__ (self):
        super (RecordKeyNode, self).__init__ ()
        self._add_fields ([
            Field ('type'),
            Field ('value')
        ])


class RecordKey (DescriptionNode):
    def __init__ (self):
        super (RecordKey, self).__init__ ()
        self._add_fields ([
            Field ('key'),
            Field ('type'),
            Field ('default', RecordKeyNode ())
        ])


class Record (DescriptionNode):
    def __init__ (self):
        super (Record, self).__init__ ()
        self._add_fields ([
            Field ('keys', TypedList (RecordKey)),
            Field ('type_name'),
            Field ('input_type'),
            Field ('type_full_name')
        ])


class AbstractRecord (Record):
    def __init__ (self):
        super (AbstractRecord, self).__init__ ()
        self._add_fields ([
            Field ('implementations')
        ])


class ProfilerJSONDecoder (json.JSONDecoder):
    def decode (self, json_string):
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)
        lst = TypedList ()
        lst.parse (default_obj)
        return lst


json_location = 'example.json'
with open (json_location, 'r') as fp:
    jsonObj = json.load (fp, encoding="utf-8", cls=ProfilerJSONDecoder)
    print jsonObj

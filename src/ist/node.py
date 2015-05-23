# encoding: utf-8
# author:   Jan Hybs


import json


class TypedList(list):
    def __init__(self, cls=None, *args, **kwargs):
        self.cls = cls
        list.__init__(self, *args, **kwargs)

    def parse (self, lst):
        if self.cls is None:
            for o in lst:
                if o.get('input_type', '') == 'Record':
                    self.append(Record(o))
                else:
                    self.append (o)
        else:
            for o in lst:
                self.append(self.cls(o))


class AbstractNode(object):
    def __init__(self, o=None):
        self.id = None


class ComplexNode(AbstractNode):
    def __init__(self, o=None):
        super(ComplexNode, self).__init__(o)
        self.name = None
        self.description = None


class RecordKeyNode(AbstractNode):
    def __init__(self, o=None):
        super(RecordKeyNode, self).__init__(o)
        self.type = None
        self.value = None


class RecordKey(AbstractNode):
    def __init__(self, o=None):
        super(RecordKey, self).__init__(o)
        self.key = None
        self.description = None
        self.type = None
        self.default = TypedList(RecordKeyNode)
        self.default.parse(o.get('default', []))


class Record(ComplexNode):
    def __init__(self, o=None):
        super(Record, self).__init__(o)
        self.keys = TypedList(RecordKey)
        self.keys.parse(o.get('keys', []))


class ProfilerJSONDecoder (json.JSONDecoder):

    def decode (self, json_string):
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)
        lst = TypedList()
        lst.parse(default_obj)
        return lst


json_location = 'example.json'
with open (json_location, 'r') as fp:
    jsonObj = json.load (fp, encoding="utf-8", cls=ProfilerJSONDecoder)
    print jsonObj

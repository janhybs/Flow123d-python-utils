# encoding: utf-8
# author:   Jan Hybs
from ist.globals import Globals
from ist.utils.utils import Field, TypedList


class ISTNode (object):
    _fields = []

    def parse (self, o={ }):
        for field in self._fields:
            # parse list
            if issubclass (field.type, TypedList):
                value = field.value.copy ().parse (o.get (field.name, []))
            # parse more complex objects
            elif issubclass (field.type, ISTNode):
                value = field.value.copy ().parse (o.get (field.name, { }))
            # simple values
            else:
                value = o.get (field.name)

            # create attribute on class instance
            self.__setattr__ (field.name, value)
            if field.name == 'id' and value is not None:
                Globals.items[value] = self

        return self


    def copy (self):
        return self.__class__()

    def __repr__ (self):
        return '<{self.__class__.__name__} {self._fields}>'.format (self=self)


class Reference (ISTNode):
    def parse (self, o=''):
        self.ref_id = o
        return self

    def get_reference (self):
        return Globals.items.get (self.ref_id, None)

    def copy (self):
        return Reference ()

    def __repr__ (self):
        return "<Reference ({self.ref_id}) -> {ref}>".format (self=self, ref=self.get_reference ())


class NumberRange (ISTNode):
    def parse (self, o=[]):
        try:
            self.min = o[0]
        except:
            self.min = None

        try:
            self.max = o[1]
        except:
            self.max = None

        return self

    def __repr__ (self):
        return '<NumberRange {{{self.min} , {self.max}}}>'.format (self=self)


class AbstractNode (ISTNode):
    _fields = ISTNode._fields + [
        Field ('id'),
        Field ('input_type')
    ]


class DescriptionNode (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('description')
    ]


class RecordKeyNode (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('type'),
        Field ('value')
    ]


class RecordKey (DescriptionNode):
    _fields = DescriptionNode._fields + [
        Field ('key'),
        Field ('type', Reference ()),
        Field ('default', RecordKeyNode ())
    ]


class Record (DescriptionNode):
    _fields = DescriptionNode._fields + [
        Field ('type_name'),
        Field ('input_type'),
        Field ('type_full_name'),
        Field ('keys', TypedList (RecordKey)),
        Field ('implements', TypedList (Reference))
    ]


class AbstractRecord (Record):
    _fields = Record._fields + [
        Field ('implementations', TypedList (Reference)),
        Field ('default_descendant', Reference ()),
        Field ('full_name'),
        Field ('name')
    ]


class SelectionValue (DescriptionNode):
    _fields = AbstractNode._fields + [
        Field ('name')
    ]


class Selection (DescriptionNode):
    _fields = DescriptionNode._fields + [
        Field ('values', TypedList (SelectionValue)),
        Field ('name'),
        Field ('full_name')
    ]


class String (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('name'),
        Field ('full_name')
    ]


class Double (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('name'),
        Field ('full_name'),
        Field ('range', NumberRange ())
    ]


class Integer (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('name'),
        Field ('full_name'),
        Field ('range', NumberRange ())
    ]


class FileName (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('name'),
        Field ('full_name'),
        Field ('file_mode')
    ]


class Bool (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('name'),
        Field ('full_name')
    ]


class Array (AbstractNode):
    _fields = AbstractNode._fields + [
        Field ('range', NumberRange ()),
        Field ('subtype', Reference ())
    ]


registered_nodes = {
    'Record': Record,
    'AbstractRecord': AbstractRecord,
    'Selection': Selection,
    'String': String,
    'Double': Double,
    'Integer': Integer,
    'FileName': FileName,
    'Bool': Bool,
    'Array': Array
}



# ['', u'Selection', u'String', u'Double', u'FileName', u'Record', u'Bool', u'Integer', u'Array', u'AbstractRecord']
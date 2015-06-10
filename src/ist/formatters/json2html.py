# encoding: utf-8
# author:   Jan Hybs
from ist.nodes import Integer, String, DescriptionNode, ISTNode
from ist.utils.htmltree import htmltree


class HTMLItemFormatter(htmltree):
    def __init__(self, cls):
        super(HTMLItemFormatter, self).__init__('section', cls)


class HTMLUniversal(HTMLItemFormatter):
    def __init__(self):
        super(HTMLUniversal, self).__init__(cls='selection')

    def _start_format_as_child(self, self_object, record_key, record):
        self.h3(record.type_name + '::' + record_key.key)

    def _format_as_child(self, self_object, record_key, record):
        raise Exception('Not implemented yet')

    def _end_format_as_child(self, self_object, record_key, record):
        self.add(HTMLRecordKeyDefault().format_as_child(record_key.default, record_key, record))
        self.description(record_key.description)


    def format_as_child(self, self_object, record_key, record):
        self._start_format_as_child(self_object, record_key, record)
        self._format_as_child(self_object, record_key, record)
        self._end_format_as_child(self_object, record_key, record)


class HTMLRecordKeyDefault(object):
    def __init__(self):
        self.format_rules = {
            'value at read time': self.raw_format,
            'value at declaration': self.textlangle_format,
            'optional': self.textlangle_format,
            'obligatory': self.textlangle_format
        }

    def format_as_child(self, self_default, record_key, record):
        method = self.format_rules.get(self_default.type, None)
        if method:
            return method(self_default, record_key, record)

        return HTMLRecordKeyDefault.textlangle_format(self_default, record_key, record)

    def textlangle_format(self, self_default, record_key, record):
        html = htmltree('div', 'record-key-default')
        html.italic(self_default.value)
        return html.current()

    def raw_format(self, self_default, record_key, record):
        html = htmltree('div', 'record-key-default')
        html.bold(self_default.value)
        return html.current()


class HTMLInteger(HTMLUniversal):
    def _format_as_child(self, self_int, record_key, record):
        self.span('Integer: ')
        self.bold(str(self_int.range))


class HTMLDouble(HTMLUniversal):
    def _format_as_child(self, self_double, record_key, record):
        self.span('Double: ')
        self.bold(str(self_double.range))


class HTMLBool(HTMLUniversal):
    def _format_as_child(self, self_bool, record_key, record):
        pass


class HTMLString(HTMLUniversal):
    def _format_as_child(self, self_fn, record_key, record):
        self.span('String (generic)')


class HTMLFileName(HTMLUniversal):
    def _format_as_child(self, self_fn, record_key, record):
        self.span((self_fn.file_mode + ' file name'))


class HTMLArray(HTMLUniversal):
    def _format_as_child(self, self_array, record_key, record):
        subtype = self_array.subtype.get_reference()

        if type(subtype) == Integer:
            self.span('Array of {subtype} {subrange}'.format(
                range=self_array.range, subtype=subtype.input_type,
                subrange=subtype.range))
        else:
            self.span('Array{range} of {subtype}'.format(
                range=' ' + str(self_array.range) if not self_array.range.is_pointless() else '',
                subtype=subtype.input_type))

        if type(subtype) == String:
            self.span(' (generic)')

        if issubclass(subtype.__class__, DescriptionNode):
            self.span(': ')
            self.href(subtype.get('type_name', 'name'))  # TODO href
        else:
            # no link
            pass


class HTMLSelection(HTMLItemFormatter):
    def __init__(self):
        super(HTMLSelection, self).__init__(cls='selection')

    def format_as_child(self, self_selection, record_key, record):
        self.h3(record.type_name + '::' + record_key.key)

        self.span('selection: ')
        with self.open('strong'):
            if self_selection.include_in_format():
                self.href(self_selection.name)
            else:
                self.span(self_selection.name)

        self.span('default value:')
        self.description(record_key.description)


    def format(self, selection):
        self.h2(selection.name)
        self.description(selection.description)

        with self.open('ul'):
            for selection_value in selection.values:
                with self.open('li'):
                    self.h3(selection_value.name)
                    self.description(selection_value.description)

        return self


class HTMLAbstractRecord(HTMLItemFormatter):
    def __init__(self):
        super(HTMLAbstractRecord, self).__init__(cls='abstract-record')

    def format_as_child(self, abstract_record, record_key, record):
        self.h3(record.type_name + '::' + record_key.key)
        self.span('abstract type: ')

        with self.open('strong'):
            self.href(abstract_record.name)

        self.add(HTMLRecordKeyDefault().format_as_child(record_key.default, record_key, record))
        self.description(record_key.description)

    def format(self, abstract_record):
        self.h2(abstract_record.name)

        if abstract_record.default_descendant:
            reference = abstract_record.default_descendant.get_reference()
            self.href(reference.type_name)
            self.description(abstract_record.name)

        self.description(abstract_record.description)

        for descendant in abstract_record.implementations:
            with self.open('h3'):
                self.span('Descendant')
                self.href(descendant.get_reference().type_name)


class HTMLRecord(HTMLItemFormatter):
    def __init__(self):
        super(HTMLRecord, self).__init__(cls='record')

    def format_as_child (self, self_record, record_key, record):
        self.h3(record.type_name + '::' + record_key.key)
        self.span('record: ')

        with self.open('strong'):
            self.href(self_record.type_name)

        self.add(HTMLRecordKeyDefault().format_as_child(record_key.default, record_key, record))
        self.description(record_key.description)

    def format(self, record):
        reference_list = record.implements
        self.h2(record.type_name)

        # TODO what if multiple inheritance? list
        if reference_list:
            for reference in reference_list:
                self.href(reference.get_reference().name)

        if record.reducible_to_key:
            self.href(record.type_name + '::' + record.reducible_to_key)

        self.description(record.description)

        for record_key in record.keys:
            fmt = HTMLFormatter.get_formatter_for(record_key)
            fmt.format(record_key, record)
            self.add(fmt.current())


class HTMLRecordKey(HTMLItemFormatter):
    def __init__(self):
        super(HTMLRecordKey, self).__init__(cls='record-key')

    def format(self, record_key, record):
        reference = record_key.type.get_reference()

        # try to grab formatter and format type and default value based on reference type
        try:
            fmt = HTMLFormatter.get_formatter_for(reference)
            fmt.format_as_child(reference, record_key, record)
            self.add(fmt.current())
        except Exception as e:
            print ' <<Missing formatter for {}>>'.format(type(reference))
            print e


class HTMLFormatter(object):
    formatters = {
        'Record': HTMLRecord,
        'RecordKey': HTMLRecordKey,
        'AbstractRecord': HTMLAbstractRecord,
        'String': HTMLString,
        'Selection': HTMLSelection,
        'Array': HTMLArray,
        'Integer': HTMLInteger,
        'Double': HTMLDouble,
        'Bool': HTMLBool,
        'FileName': HTMLFileName,
        '': HTMLUniversal
    }

    @staticmethod
    def format(items):
        html = htmltree('div')

        for item in items:
            # format only IST nodes
            if issubclass(item.__class__, ISTNode):

                # do no format certain objects
                if not item.include_in_format():
                    continue

                try:
                    fmt = HTMLFormatter.get_formatter_for(item)
                    fmt.format(item)
                    html.add(fmt.current())
                except Exception as e:
                    # print e
                    continue

        return html

    @staticmethod
    def get_formatter_for(o):
        cls = HTMLFormatter.formatters.get(o.__class__.__name__, None)
        if cls is None:
            cls = HTMLFormatter.formatters.get('')
        return cls()

# encoding: utf-8
# author:   Jan Hybs
from ist.nodes import Integer, String, DescriptionNode, ISTNode, ComplexNode
from ist.utils.htmltree import htmltree


class HTMLItemFormatter(htmltree):
    def __init__(self, cls):
        super(HTMLItemFormatter, self).__init__('section', cls)


class HTMLUniversal(HTMLItemFormatter):
    def __init__(self):
        super(HTMLUniversal, self).__init__(cls='simple-element')

    def _start_format_as_child(self, self_object, record_key, record):
        self.h(record_key.key, record.type_name)

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
        with html.open('div'):
            html.span('Default: ')
            with html.open('span', attrib={ 'class': 'header-info skew' }):
                if len(str(self_default.value)):
                    html.span(self_default.value)
                else:
                    html.span(self_default.type)

        return html.current()

    def raw_format(self, self_default, record_key, record):
        html = htmltree('div', 'record-key-default')
        with html.open('div'):
            html.span('Default: ')
            with html.open('span', attrib={ 'class': 'skew' }):
                if len(str(self_default.value)):
                    html.span(self_default.value)
                else:
                    html.span(self_default.type)
        return html.current()


class HTMLInteger(HTMLUniversal):
    def _format_as_child(self, self_int, record_key, record):
        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('Integer: ')
            self.span(str(self_int.range))


class HTMLDouble(HTMLUniversal):
    def _format_as_child(self, self_double, record_key, record):
        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('Double: ')
            self.span(str(self_double.range))


class HTMLBool(HTMLUniversal):
    def _format_as_child(self, self_bool, record_key, record):
        pass


class HTMLString(HTMLUniversal):
    def _format_as_child(self, self_fn, record_key, record):
        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('String (generic)')


class HTMLFileName(HTMLUniversal):
    def _format_as_child(self, self_fn, record_key, record):
        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span((self_fn.file_mode + ' file name'))


class HTMLArray(HTMLUniversal):
    def _format_as_child(self, self_array, record_key, record):
        subtype = self_array.subtype.get_reference()
        with self.open('span', ' ', attrib={ 'class': 'header-info skew' }):

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
                self.link(subtype.get('type_name', 'name'))  # TODO href
            else:
                # no link
                pass


class HTMLSelection(HTMLItemFormatter):
    def __init__(self):
        super(HTMLSelection, self).__init__(cls='selection')

    def format_as_child(self, self_selection, record_key, record):
        self.root.attrib['class'] = 'child-selection'
        self.h(record_key.key, record.type_name)

        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('selection: ')
            if self_selection.include_in_format():
                self.link(self_selection.name)
            else:
                self.span(self_selection.name)

        with self.open('div'):
            self.span('default value:')
            with self.open('span', attrib={ 'class': 'header-info skew' }):
                self.span(record_key.default.value)

        self.description(record_key.description)


    def format(self, selection):
        with self.open('header'):
            self.h2(selection.name)
            self.description(selection.description)

        with self.open('ul', attrib={ 'class': 'item-list' }):
            for selection_value in selection.values:
                with self.open('li'):
                    self.h(selection_value.name)
                    self.description(selection_value.description)

        return self


class HTMLAbstractRecord(HTMLItemFormatter):
    def __init__(self):
        super(HTMLAbstractRecord, self).__init__(cls='abstract-record')

    def format_as_child(self, abstract_record, record_key, record):
        self.root.attrib['class'] = 'child-abstract-record'
        self.h(record_key.key, abstract_record.name)

        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('abstract type: ')
            self.link(abstract_record.name)

        self.add(HTMLRecordKeyDefault().format_as_child(record_key.default, record_key, record))
        self.description(record_key.description)

    def format(self, abstract_record):
        with self.open('header'):
            self.h2(abstract_record.name)

            if abstract_record.default_descendant:
                reference = abstract_record.default_descendant.get_reference()
                self.link(reference.type_name)
                self.description(abstract_record.name)

            self.description(abstract_record.description)

        self.italic('Descendants')
        with self.open('ul', attrib={ 'class': 'item-list' }):
            for descendant in abstract_record.implementations:
                reference = descendant.get_reference()
                with self.open('li'):
                    self.link(reference.type_name)
                    self.span(' - ')
                    self.span(reference.description)


class HTMLRecord(HTMLItemFormatter):
    def __init__(self):
        super(HTMLRecord, self).__init__(cls='record')

    def format_as_child(self, self_record, record_key, record):
        self.root.attrib['class'] = 'child-record'
        self.h(record_key.key, record.type_name)

        with self.open('span', attrib={ 'class': 'header-info skew' }):
            self.span('record: ')
            self.link(self_record.type_name)

        self.add(HTMLRecordKeyDefault().format_as_child(record_key.default, record_key, record))
        self.description(record_key.description)

    def format(self, record):
        reference_list = record.implements
        with self.open('header'):
            self.h2(record.type_name)

            if reference_list:
                for reference in reference_list:
                    self.italic('implements abstract type: ')
                    self.link(reference.get_reference().name)

            if record.reducible_to_key:
                self.italic('constructible from key: ')
                self.link(record.reducible_to_key, ns=record.type_name)

            self.description(record.description)

        with self.open('ul', attrib={ 'class': 'item-list' }):
            for record_key in record.keys:

                if not record_key.include_in_format():
                    continue

                with self.open('li'):
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
        html.id('input-reference')

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

    @staticmethod
    def navigation_bar(items):
        html = htmltree('div')

        html.bold('Records: ')
        HTMLFormatter._add_items(items, html, 'Record')

        html.bold('Abstract record: ')
        HTMLFormatter._add_items(items, html, 'AbstractRecord')

        html.bold('Selections: ')
        HTMLFormatter._add_items(items, html, 'Selection')

        return html

    @staticmethod
    def _add_items (items, html, type=None):
        with html.open('ul', attrib={ 'class': 'nav-bar' }):
            for item in items:
                if issubclass(item.__class__, ComplexNode):
                    # do no format certain objects
                    if not item.include_in_format():
                        continue

                    if type and not item.input_type == type :
                        continue

                    with html.open('li'):
                        with html.open('a', '', html.generate_href(item.get_name())):
                            html.span(item.get_type()[0], attrib={ 'class': 'shortcut' })
                            html.span(item.get_name())
# encoding: utf-8
# author:   Jan Hybs
import cgi

import xml.etree.ElementTree as ET
import re


class htmltree(object):
    def __init__(self, tag_name='div', cls='', *args, **kwargs):
        self.attrib = { 'class': cls } if cls else { }
        self.tag_name = tag_name
        self.root = ET.Element(tag_name, self.attrib)
        self.counter = 0
        self.roots = [self.root]

    def tag(self, tag_name, value='', attrib={ }):
        element = ET.Element(tag_name, attrib)
        element.text = cgi.escape(value)
        self.current().append(element)
        return element

    def current(self):
        return self.roots[self.counter]

    def add(self, element):
        return self.current().append(element)

    def h(self, title, subtitle='', level='h3'):
        if subtitle:
            with self.open(level, '', self.generate_id(title, subtitle)):
                with self.open('small'):
                    self.tag('a', subtitle + '', self.generate_href(subtitle))
                    self.span('::')
                self.span(title)

    def h1(self, value='', attrib={ }):
        return self.tag('h1', value, attrib)

    def h2(self, value='', attrib={ }):
        attrib.update(self.generate_id(value))
        self.tag('h2', value, attrib)

    def h3(self, value='', attrib={ }):
        return self.tag('h3', value, attrib)

    def h4(self, value='', attrib={ }):
        return self.tag('h4', value, attrib)

    def h5(self, value='', attrib={ }):
        return self.tag('h5', value, attrib)

    def h6(self, value='', attrib={ }):
        return self.tag('h6', value, attrib)

    def ul(self, value='', attrib={ }):
        return self.tag('ul', value, attrib)

    def ol(self, value='', attrib={ }):
        return self.tag('ol', value, attrib)

    def span(self, value='', attrib={ }):
        return self.tag('span', value, attrib)

    def div(self, value='', attrib={ }):
        return self.tag('div', value, attrib)

    def bold(self, value='', attrib={ }):
        return self.tag('strong', value, attrib)

    def italic(self, value='', attrib={ }):
        return self.tag('em', value, attrib)

    def li(self, value='', attrib={ }):
        return self.tag('li', value, attrib)

    def link(self, target, text='', ns=''):
        return self.tag('a', text if text else target, self.generate_href(target, ns))

    def open(self, tag_name, value='', attrib={ }):
        element = self.tag(tag_name, value, attrib)
        self.roots.append(element)
        return self

    def description(self, value):
        if value:
            return self.tag('div', value, { 'class': 'description' })

        return self.tag('div', 'no description provided', { 'class': 'description no-description' })

    def __enter__(self):
        self.counter += 1
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.counter -= 1
        self.roots.pop()
        return self

    def dump(self):
        return ET.tostring(self.root, method='html')

    def __repr__(self):
        return '<htmltree object>'

    def style(self, location):
        self.tag('link', '', { 'rel': 'stylesheet', 'type': 'text/css', 'media': 'screen', 'href': location })

    def script(self, location):
        self.tag('script', '', { 'type': 'text/js', 'src': location })

    def id(self, id):
        self.root.attrib['id'] = id

    def _chain_values(self, value, sub_value=''):
        return self._secure(value if not sub_value else sub_value + '-' + value)

    def generate_id(self, value, sub_value=''):
        return { 'id': self._chain_values(value, sub_value) }

    def generate_href(self, value, sub_value=''):
        return { 'href': '#' + self._chain_values(value, sub_value) }

    def _secure(self, value=''):
        value = re.sub(r'\W+', '-', value)
        value = re.sub(r'-$', '', value)
        return value
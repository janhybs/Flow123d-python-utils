# encoding: utf-8
# author:   Jan Hybs

import xml.etree.ElementTree as ET


class htmltree(object):
    def __init__(self, tag_name='div', *args, **kwargs):
        self.root = ET.Element(tag_name)
        self.counter = 0
        self.roots = [self.root]

    def tag(self, tag_name, value='', attrib={ }):
        element = ET.Element(tag_name, attrib)
        element.text = value
        self.current().append(element)
        return element

    def current(self):
        return self.roots[self.counter]

    def h1(self, value='', attrib={ }):
        return self.tag('h1', value, attrib)

    def h2(self, value='', attrib={ }):
        return self.tag('h2', value, attrib)

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

    def li(self, value='', attrib={ }):
        return self.tag('li', value, attrib)

    def open(self, tag_name, value='', attrib={ }):
        element = self.tag(tag_name, value, attrib)
        self.roots.append(element)
        return self

    def description(self, value):
        return self.tag('div', value, { 'class': 'description' })

    def __enter__(self):
        self.counter += 1
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.counter -= 1
        self.roots.pop()
        return self

    def dump(self):
        return ET.dump(self.root)

    def __repr__(self):
        return '<htmltree object>'



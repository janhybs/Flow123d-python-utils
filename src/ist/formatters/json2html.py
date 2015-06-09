# encoding: utf-8
# author:   Jan Hybs
from ist.utils.htmltree import htmltree


class HTMLFormatter(htmltree):
    def __init__(self):
        super(htmltree, self).__init__(tag_name='section')


class HTMLSelection(HTMLFormatter):
    def __init__(self):
        super(HTMLFormatter, self).__init__()

    def format (self, selection):
        self.h1(selection.name)
        self.description (selection.description)
        return self
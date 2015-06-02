# encoding: utf-8
# author:   Jan Hybs


'''
FlowLinks Extension for Python-Markdown
======================================

Converts [[type_value]] to relative links.
'''

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import re


def build_url (label, base, end):
    """ Build a url from the label, a base, and an end. """
    clean_label = re.sub (r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '%s%s%s' % (base, clean_label, end)


class FlowLinkExtension (Extension):
    def __init__ (self, *args, **kwargs):
        self.config = {
        }

        super (FlowLinkExtension, self).__init__ (*args, **kwargs)

    def extendMarkdown (self, md, md_globals):
        self.md = md

        # append to end of inline patterns
        # WIKILINK_RE = r'\[\[([\w0-9_ -]+)\]\]'
        WIKILINK_RE = r'\[\[([\w0-9-]+_[\w0-9_-]+)\]\]'
        wikilinkPattern = FlowLinks (WIKILINK_RE, self.getConfigs ())
        wikilinkPattern.md = md
        md.inlinePatterns.add ('wikilink', wikilinkPattern, "<not_strong")


class FlowLinks (Pattern):
    def __init__ (self, pattern, config):
        super (FlowLinks, self).__init__ (pattern)
        self.config = config

    def handleMatch (self, m):
        print m
        if m.group (2).strip ():
            label = m.group (2).strip ()
            (type, name) = label.split ("_", 1)
            element = self.build_element(type, name)
            return element
        else:
            return ''

    def build_element (self, type, value):
        if type.lower () == 'attribute':
            p = etree.Element ('p')
            p.text = 'attribute value here'
            return p

        if type.lower () in ('record', 'abstractrecord', 'selection'):
            a = etree.Element ('a')
            a.text = value
            a.set('href', value)
            return a

        print 'unknown type'
        return None


def makeExtension (*args, **kwargs):
    return FlowLinkExtension (*args, **kwargs)

# encoding: utf-8
# author:   Jan Hybs

#
# import json
# from ist.formatters.latex import LatexRecord, LatexFormatter
# from ist.nodes import TypedList, Array
# from ist.nodes import Record, AbstractRecord, Selection
#
#
# class ProfilerJSONDecoder (json.JSONDecoder):
# def decode (self, json_string):
# default_obj = super (ProfilerJSONDecoder, self).decode (json_string)
# lst = TypedList ()
# lst.parse (default_obj)
# return lst
#
#
# json_location = 'example.json'
# with open (json_location, 'r') as fp:
# # parse json file
# jsonObj = json.load (fp, encoding="utf-8", cls=ProfilerJSONDecoder)
#
# result = LatexFormatter.format (jsonObj)
# result = ''.join(result)
#
#     with open ('../../docs/input_reference_red.tex', 'w') as fp:
#         fp.write (result)
#
#

from markdown import markdown
import xml.etree.ElementTree as ET
from ist.utils.texlist import texlist

latex = """
**foo** *em* [link](g.com)

* cascas
* caas
* caas
"""
html = markdown (latex)

tree = ET.fromstring ('<html>' + html + "</html>")


class LatexHref (object):
    def to_latex (self, element):
        tex = texlist ()
        with tex:
            tex.append ('\\href')
            tex.add (element.attrib.get ('href'))
            tex.add (element.text)
        return tex


class Html2Latex (object):
    def to_latex (self, element):
        tex = texlist ()

        if element.tag == 'li':
            with tex:
                tex.append ('\\item ')
                tex.append (element.text)

        if element.tag == 'a':
            tex.extend (LatexHref ().to_latex (element))

        if element.tag == 'em':
            with tex:
                tex.tag ('it', element.text)

        if element.tag == 'strong':
            with tex:
                tex.tag ('bf', element.text)

        if element.tag == 'ul':
            tex.append ('\\begin{itemize}')
            tex.newline ()

        if element.tag == 'ol':
            tex.append ('\\begin{enumerate}')
            tex.newline ()

        # tex.append (element)
        for child in element:
            tex.extend (Html2Latex ().to_latex (child))

        if element.tag == 'ul':
            tex.append ('\\end{itemize}')

        if element.tag == 'ol':
            tex.append ('\\end{enumerate}')

        if element.tag == 'li':
            tex.newline ()

        if element.tail:
            tex.append (element.tail)

        return tex


tex = Html2Latex ().to_latex (tree)
print tex
print html
print ''.join (tex)
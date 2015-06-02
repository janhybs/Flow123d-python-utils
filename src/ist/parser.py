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
# with open ('../../docs/input_reference_red.tex', 'w') as fp:
# fp.write (result)
#
#

from markdown import markdown
import xml.etree.ElementTree as ET
from ist.formatters.html2latex import Html2Latex
from ist.utils.texlist import texlist

latex = """
# foo
**strong** *em* [link](g.com)            ***strong-italic***

If you can **please** do *this*:

* hi
* hello
* greetings


meaning __this__:

1. foo
2. bar
3. stuff

stuff

```
x = 0
x = 2 + 2
what is x
```
"""
html = markdown (latex, extensions=['markdown.extensions.sane_lists', 'markdown.extensions.nl2br'])
tree = ET.fromstring ('<html>' + html + "</html>")



tex = Html2Latex (tree).to_latex ()
print tex
print html
print ''.join (tex)
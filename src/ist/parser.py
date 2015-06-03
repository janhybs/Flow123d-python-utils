# encoding: utf-8
# author:   Jan Hybs

#
import json
from ist.formatters.json2latex import LatexRecord, LatexFormatter
from ist.globals import Globals
from ist.nodes import TypedList, Array
from ist.nodes import Record, AbstractRecord, Selection


class ProfilerJSONDecoder (json.JSONDecoder):
    def decode (self, json_string):
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)
        lst = TypedList ()
        lst.parse (default_obj)
        return lst


json_location = 'example.json'
with open (json_location, 'r') as fp:
    # parse json file
    jsonObj = json.load (fp, encoding="utf-8", cls=ProfilerJSONDecoder)

result = LatexFormatter.format (jsonObj)




import xml.etree.ElementTree as ET
import markdown
from ist.formatters.html2latex import Html2Latex
from ist.utils.texlist import texlist

latex = """
# Simple md support

showcase of **strong** and *em* fonts (or ***both***), links to [Google](google.com)

**Simple** *lists*:

* hi
* hello
* greetings


Also numbered:

1. foo
2. bar
3. stuff

also code support:

```
x = 0
x = 2 + 2
what is x
```

Additionally link to Records, AbstractRecords and Selections. You can also **reference** their fields (for example record key)

link to [[record_root]] and its key: [[record_root#keys#problem]] looks like this

or like this:

- [[record_root#keys#pause_after_run]]
- [[record_root#keys#problem]]
- [[record_SequentialCoupling]]
- [[selection_PartTool]]
- [[record_SoluteTransport_DG_Data#keys#diff_m]]

"""
html = markdown.markdown (latex, extensions=[
    'markdown.extensions.sane_lists',
    'markdown.extensions.nl2br',
    'ist.formatters.extensions.flowlinks'

])
tree = ET.fromstring ('<html>' + html + "</html>")



tex = Html2Latex (tree).to_latex ()
print '\n\n'
print html
print '\n\n'
print ''.join (tex)


result.extend (tex)
result = ''.join(result)

with open ('../../docs/input_reference_red.tex', 'w') as fp:
    fp.write (result)

# encoding: utf-8
# author:   Jan Hybs

#
import json
import sys
from ist.formatters.extensions.md_latex import MdLatexSupport
from ist.formatters.json2html import HTMLSelection, HTMLInteger, HTMLFormatter
from ist.formatters.json2latex import LatexRecord, LatexFormatter
from ist.globals import Globals
from ist.nodes import TypedList, Array
from ist.nodes import Record, AbstractRecord, Selection

import xml.etree.ElementTree as ET
import markdown
from ist.formatters.html2latex import Html2Latex

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


html = HTMLFormatter.format(jsonObj)
# def f (o):
#     print o
#     for ch in o._children:
#         f (ch)
#
# f (html.current())
print html.dump()
sys.exit(0)

from ist.utils.texlist import texlist

markdown_example = """
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

Using latex in md:

(( \\textbf{bold} and \\textit{italic} font ))

or like this: (( $x=\\frac{1+y}{1+2z^2}$ )) bigger?


(( $$x=\\frac{1+y}{1+2z^2}$$ ))

or

(($$
 \\frac{1}{\displaystyle 1+
   \\frac{1}{\displaystyle 2+
   \\frac{1}{\displaystyle 3+x}}} +
 \\frac{1}{1+\\frac{1}{2+\\frac{1}{3+x}}}
$$))

or

((
\\begin{eqnarray*}
 e^x &\\approx& 1+x+x^2/2! + \\\\
   && {}+x^3/3! + x^4/4! + \\\\
   && + x^5/5!
\\end{eqnarray*}
))

ca
asc

"""

md_latex = MdLatexSupport ()
markdown_example = md_latex.prepare (markdown_example)
html_example = markdown.markdown (markdown_example, extensions=[
    'markdown.extensions.sane_lists',
    'markdown.extensions.nl2br',
    'ist.formatters.extensions.md_links'])
html_example = md_latex.finish (html_example)
tree = ET.fromstring ('<html_example>' + html_example + "</html_example>")

tex = Html2Latex (tree).to_latex ()
print '\n\n'
print html_example
print '\n\n'
print ''.join (tex)

result.extend (tex)
result = ''.join (result)

with open ('../../docs/input_reference_red.tex', 'w') as fp:
    fp.write (result)
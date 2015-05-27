# encoding: utf-8
# author:   Jan Hybs

#
import json
from ist.formatters.latex import LatexRecord, LatexFormatter
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

    print jsonObj[2]
    result = LatexFormatter.format ([jsonObj[2]])
    result = ''.join(result)

    with open ('../../docs/input_reference_red.tex', 'w') as fp:
        fp.write (result)



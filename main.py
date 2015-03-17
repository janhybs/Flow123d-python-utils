import sys
import json
import datetime



__author__ = 'Jan Hybs'

intFields = ["file-line", "call-count", "call-count-min", "call-count_max", "call-count_sum"]
floatFields = ["cumul-time", "cumul-time-min", "cumul-time_max", "cumul-time_sum", "percent"]
intFieldsRoot = ["task-size", "run-process-count"]
floatFieldsRoot = ["timer-resolution"]
dateFields = ["run-started-at", "run-finished-at"]


class ProfilerJSONDecoder (json.JSONDecoder) :
    def decode (self, json_string) :
        """
        json_string is basicly string that you give to json.loads method
        """
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)

        convertFieldsTo (default_obj, intFields, int)
        convertFieldsTo (default_obj, floatFields, float)
        convertFieldsTo (default_obj, intFieldsRoot, int, False)
        convertFieldsTo (default_obj, floatFieldsRoot, float, False)
        convertFieldsTo (default_obj, dateFields, parseDate, False)

        return default_obj

def default(obj):
    """Default JSON serializer."""
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%m/%d/%y %H:%M:%S")
    return str (obj)

def parseDate (str):
    return datetime.datetime.strptime(str, "%m/%d/%y %H:%M:%S")


def getClassInstance (cls):
    module = __import__(cls)
    class_ = getattr(module, cls)
    instance = class_()
    return instance

def convertFieldsTo (obj, fields, fun, rec=True) :
    for field in fields :
        for prop in obj :
            if prop == field :
                obj[prop] = fun (obj[prop])
    if rec :
        try :
            for child in obj["children"] :
                convertFieldsTo (child, fields, fun)
        except :
            pass


if __name__ == "__main__" :
    fp = open ("./logs/profiler_info_15.03.17_11-19-04.log.json")
    jsonObj = json.load (fp, encoding="utf-8", cls=ProfilerJSONDecoder)
    fp.close ()
    fp = open ("a.json", "w")
    json.dump (jsonObj, fp, indent=4, default=default)
    fp.close ()

    getClassInstance("SimpleTableFormatter").format(jsonObj)

    sys.exit (0)
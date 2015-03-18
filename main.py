import sys
import json
import datetime
import importlib
from optparse import OptionParser



__author__ = 'Jan Hybs'

intFields = ["file-line", "call-count", "call-count-min", "call-count_max", "call-count_sum"]
floatFields = ["cumul-time", "cumul-time-min", "cumul-time_max", "cumul-time_sum", "percent"]
intFieldsRoot = ["task-size", "run-process-count"]
floatFieldsRoot = ["timer-resolution"]
dateFields = ["run-started-at", "run-finished-at"]

parser = OptionParser()
parser.add_option("-i", "--input", dest="input", metavar="FILENAME", default=None,
                  help="Absolute or relative path to JSON file which will be processed")
parser.add_option("-o", "--output", dest="output", metavar="FILENAME", default=None,
                  help="Absolute or relative path output file which will be generated/overwritten")
parser.add_option("-f", "--formatter", dest="formatter", metavar="CLASSNAME", default="SimpleTableFormatter",
                  help="Classname of formatter which will be used, to list available formatters use option -l (--list)")
parser.add_option("-l", "--list", dest="list", default=False, action="store_true",
                  help="Prints all formatters available in folder formatters (using duck-typing)")
parser.add_option("-s", "--style", dest="styles", default=[], action="append",
                  help="Additional stylin options in name:value format (for example separator:\n default os separator)")
parser.set_usage("""%prog [options]
    """)

class ProfilerJSONDecoder (json.JSONDecoder) :
    def decode (self, json_string) :
        """
        json_string is basicly string that you give to json.loads method
        """
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)

        convert_fields (default_obj, intFields, int)
        convert_fields (default_obj, floatFields, float)
        convert_fields (default_obj, intFieldsRoot, int, False)
        convert_fields (default_obj, floatFieldsRoot, float, False)
        convert_fields (default_obj, dateFields, parse_date, False)

        return default_obj

def default(obj):
    """Default JSON serializer."""
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%m/%d/%y %H:%M:%S")
    return str (obj)

def parse_date (str):
    return datetime.datetime.strptime(str, "%m/%d/%y %H:%M:%S")


def get_class_instance (cls):
    module =  importlib.import_module("formatters." + cls)
    class_ = getattr(module, cls)
    instance = class_()
    return instance

def convert_fields (obj, fields, fun, rec=True) :
    for field in fields :
        for prop in obj :
            if prop == field :
                obj[prop] = fun (obj[prop])
    if rec :
        try :
            for child in obj["children"] :
                convert_fields (child, fields, fun)
        except :
            pass

def check_args ():
    (options, args) = parser.parse_args ()

    if options.list == True:
        return (options, args)

    if options.input == None:
        print "Error: No input file specified!"
        parser.print_help()
        sys.exit(1)

    if options.formatter == None:
        print "Error: No formatter specified!"
        parser.print_help()
        sys.exit(1)

    return (options, args)

if __name__ == "__main__" :
    (options, args) = check_args ()


    # list formatters
    if options.list == True:
        import pkgutil
        for module_loader, name, ispkg in pkgutil.iter_modules(['formatters']):
            try:
                module = importlib.import_module("formatters." + name)
                class_ = getattr(module, name)
                if getattr (class_, 'format') is not None and callable(getattr (class_, 'format')):
                    print "- {:20s}".format(name)
            except: pass
        sys.exit(0)

    # read file to JSON
    fp = open(options.input, "r")
    jsonObj = json.load(fp, encoding="utf-8", cls=ProfilerJSONDecoder)
    fp.close()


    try:
        options.styles = [value.replace ('\\n', '\n').replace ('\\t', '\t').replace ('\\r', '\r') for value in options.styles]
        options.styles = dict(item.split(":", 1) for item in options.styles)
        instance = get_class_instance (options.formatter)
        instance.set_styles (options.styles)
        output = instance.format (jsonObj)
    except Exception as e:
        print e
        sys.exit(1)

    if options.output:
        fp = open(options.output, "w")
        fp.write(output)
        fp.close()
    else:
        print output


    sys.exit (0)
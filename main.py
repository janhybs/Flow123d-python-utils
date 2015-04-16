import sys
import json
import datetime
import importlib
from optparse import OptionParser


class ProfilerTransform (object):
    __author__ = 'Jan Hybs'

    intFields = ["file-line", "call-count", "call-count-min", "call-count-max", "call-count-sum"]
    floatFields = ["cumul-time", "cumul-time-min", "cumul-time-max", "cumul-time-sum", "percent"]
    intFieldsRoot = ["task-size", "run-process-count"]
    floatFieldsRoot = ["timer-resolution"]
    dateFields = ["run-started-at", "run-finished-at"]
    parser = OptionParser()

    @staticmethod
    def parse():
        ProfilerTransform.parser.add_option("-i", "--input", dest="input", metavar="FILENAME", default=None,
                          help="Absolute or relative path to JSON file which will be processed")
        ProfilerTransform.parser.add_option("-o", "--output", dest="output", metavar="FILENAME", default=None,
                          help="Absolute or relative path output file which will be generated/overwritten")
        #ProfilerTransform.parser.add_option("-f", "--formatter", dest="formatter", metavar="CLASSNAME", default="CSVFormatter",
        ProfilerTransform.parser.add_option("-f", "--formatter", dest="formatter", metavar="CLASSNAME", default="SimpleTableFormatter",
                          help="Classname of formatter which will be used, to list available formatters use option -l (--list)")
        ProfilerTransform.parser.add_option("-l", "--list", dest="list", default=False, action="store_true",
                          help="Prints all formatters available in folder formatters (using duck-typing)")
        ProfilerTransform.parser.add_option("-s", "--style", dest="styles", default=[], action="append",
                          help="Additional styling options in name:value format (for example separator:\n default is os separator)")
        ProfilerTransform.parser.set_usage("""%prog [options]""")

        return ProfilerTransform.parser.parse_args()


    @staticmethod
    def check_args():
        (options, args) = ProfilerTransform.parse ()

        if options.list == True:
            return (options, args)

        if options.input == None:
            print "Error: No input file specified!"
            ProfilerTransform.parser.print_help()
            sys.exit(1)

        if options.formatter == None:
            print "Error: No formatter specified!"
            ProfilerTransform.parser.print_help()
            sys.exit(1)

        return (options, args)




class ProfilerJSONDecoder (json.JSONDecoder) :
    def decode (self, json_string) :
        """
        json_string is basicly string that you give to json.loads method
        """
        default_obj = super (ProfilerJSONDecoder, self).decode (json_string)

        convert_fields (default_obj, ProfilerTransform.intFields, int)
        convert_fields (default_obj, ProfilerTransform.floatFields, float)
        convert_fields (default_obj, ProfilerTransform.intFieldsRoot, int, False)
        convert_fields (default_obj, ProfilerTransform.floatFieldsRoot, float, False)
        convert_fields (default_obj, ProfilerTransform.dateFields, parse_date, False)

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


def convert (json_location, output_file, formatter):
    # return "Chyba: {} {} {}".format (json_location, output_file, formatter)
    return convert_complex (json_location, output_file, formatter, [])

def convert_complex (json_location, output_file=None, formatter="SimpleTableFormatter", styles=[]):
    # read file to JSON
    try:
        with open (json_location, 'r') as fp:
            jsonObj = json.load(fp, encoding="utf-8", cls=ProfilerJSONDecoder)
    except Exception as exception:
        # return string with message on error
        return str(exception)


    try:
        # split styles fields declaration
        styles = [value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r') for value in styles]
        styles = dict (item.split(":", 1) for item in styles)
        # grab instance and hand over styles
        instance = get_class_instance (formatter)
        instance.set_styles (styles)
        # format json object
        output = instance.format (jsonObj)
    except Exception as exception:
        # return string with message on error
        return str(exception)


    try:
        # if output file is specified write result there
        if output_file is not None:
            with open (output_file, "w") as fp:
                fp.write(output)
            print '{} file generated'.format (output_file)
        # otherwise just print result to stdout
        else:
            print output
    except Exception as exception:
        # return string with message on error
        return str(exception)


    # return True on success
    return True


def main ():
    (options, args) = ProfilerTransform.check_args()
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


    # call main method
    result = convert_complex (options.input, options.output, options.formatter, options.styles)

    # process result
    if result == True:
        sys.exit (0)
    else:
        print result
        sys.exit(1)


# only if this file is main python file, read args
if __name__ == "__main__" :
    main()
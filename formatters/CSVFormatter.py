from stringutil import StringUtil

__author__ = 'jan-hybs'
import re, os

class CSVFormatter (object) :


    def __init__(self):
        pass


    header = []
    body = []
    headerFields = ("percentage", "tag", "call count", "max time", "max/min time", "avg time", "total", "function", "location")


    def format (self, json) :
        self.json = json
        self.processHeader (json)
        self.processBody (json, 0)

        result = ""

        result += StringUtil.join (self.headerFields, separator=',', prefix='"', suffix='"') + os.linesep

        for row in self.body:
            result += StringUtil.join (row, separator=',', prefix='"', suffix='"') + os.linesep



        return result

    def set_styles (self, styles):
        pass

    def appendToHeader (self, name, value=None) :
        value = value if value is not None else self.json[name.lower ().replace (" ", "-")]
        self.header.append ((name, value))

    def appendToBody (self, values) :
        self.body.append (values)
        pass

    def processHeader (self, json) :
        self.appendToHeader ("Program name")
        self.appendToHeader ("Program version")
        self.appendToHeader ("Program branch")
        self.appendToHeader ("Program revision")
        self.appendToHeader ("Program build")

        self.appendToHeader ("Timer resolution")

        desc = re.sub ("\s+", " ", json["task-description"], re.M)
        self.appendToHeader ("Task description", desc)
        self.appendToHeader ("Task size")

        self.appendToHeader ("Run process count")
        self.appendToHeader ("Run started", json["run-started-at"])
        self.appendToHeader ("Run ended", json["run-finished-at"])
        self.appendToHeader ("Run duration", json["run-finished-at"] - json["run-started-at"])


    def processBody (self, json, level) :

        if level > 0 :
            self.appendToBody ((
                "{:1.2f}".format (json["percent"]),
                "{:s} {:s}".format ("-" * (level - 1) * 1, json["tag"]),
                "{:d}".format (json["call-count"]),
                "{:1.4f}".format (json["cumul-time-max"]),
                "{:1.4f}".format (json["cumul-time-max"] / json["cumul-time-min"]),
                "{:1.4f}".format (json["cumul-time-sum"] / json["call-count-sum"]),
                "{:1.4f}".format (json["cumul-time-sum"]),
                "{:s}:{:d}".format (json["function"], json["file-line"]),
                "{:s}".format (json["file-path"])
            ))

        try :
            for child in json["children"] :
                self.processBody (child, level + 1)
        except :
            pass
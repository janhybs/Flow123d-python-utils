from stringutil import StringUtil

__author__ = 'jan-hybs'
import re, os

class CSVFormatter (object) :


    def __init__(self):
        pass


    header = []
    body = []
    headerFields = ("percentage", "level", "tag", "call count", "max time", "max/min time", "avg time", "total", "function", "location")
    styles = {"separator": os.linesep}
    separator = os.linesep

    def format (self, json) :
        self.json = json
        # self.processHeader (json)
        self.processBody (json, 0)

        # tmpLst = []
        # tmpLst.append(self.headerFields)
        # tmpLst.extend(self.body)
        # self.maxWidth = self.fixWidth (tmpLst)

        result = ""
        result += StringUtil.join (self.headerFields, separator=',', prefix='"', suffix='"') + self.separator

        for row in self.body:
            result += StringUtil.join (row, separator=',', prefix='"', suffix='"') + self.separator



        return result



    def set_styles (self, styles):
        self.styles.update(styles)
        self.separator = self.styles["separator"]

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
                "{:d}".format (level),
                "{:s}".format (json["tag"]),
                "{:d}".format (json["call-count"]),
                "{:1.4f}".format (json["cumul-time-max"]),
                "{:1.4f}".format (json["cumul-time-max"] / json["cumul-time-min"]),
                "{:1.4f}".format (json["cumul-time-sum"] / json["call-count-sum"]),
                "{:1.4f}".format (json["cumul-time-sum"]),
                "{:s}():{:d}".format (json["function"], json["file-line"]),
                "{:s}".format (json["file-path"])
            ))

        try :
            for child in json["children"] :
                self.processBody (child, level + 1)
        except :
            pass

    def fixWidth (self, lst):
        size = len (lst[0])
        maxWidth = [5] * size

        for values in lst:
            maxWidth = [max (maxWidth[i], len (str (values[i]))) for i in range (size)]
        return maxWidth
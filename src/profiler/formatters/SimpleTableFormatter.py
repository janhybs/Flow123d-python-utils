# encoding: utf-8
# author:   Jan Hybs

import re, os, sys
from utils.dotdict import DotDict


class SimpleTableFormatter (object):
    """
    Class which takes json object from flow123d benchmark profiler report
     and returns simple table-like text string
    """

    def __init__ (self):
        self.json = None
        self.output = ""

        self.headerCols = []
        self.maxNameSize = 11

        self.bodyRows = []
        self.maxBodySize = None
        self.headerFields = ("tag", "call count", "max time", "max/min time", "avg time", "total", "source")
        self.styles = {
            "linesep": os.linesep, "padding": 0,
            "min_width": 12, "colsep": '',
            "rowsep": '', "space_header": 3,
            "leading_char": " .  "
            }

    def set_styles (self, styles):
        """Overrides default styles"""
        self.styles.update (styles)
        # make sure some values are actually ints
        self.styles["min_width"]        = int (self.styles["min_width"])
        self.styles["padding"]          = int (self.styles["padding"])
        self.styles["space_header"]     = int (self.styles["space_header"])
        self.styles["colsep_start"]     = self.styles["colsep"] + " "
        self.styles["colsep_end"]       = " " + self.styles["colsep"]

    def convert_style (self):
        self.set_styles (self.styles)
        self.styles = DotDict(self.styles)

    def format (self, json):
        """"Formats given json object"""
        self.convert_style ()


        self.json = json
        self.processHeader (json)
        self.processBody (json, 0)
        print self.maxBodySize
        self.maxBodySize = [n + self.styles.padding for n in self.maxBodySize]

        self.maxNameSize = self.maxNameSize + self.styles.space_header

        lineDivider = (sum (self.maxBodySize) + 2 + len (self.maxBodySize) * 2) * self.styles.rowsep
        fmtHead = "{{:{self.maxNameSize}s}}{{}}{self.styles.linesep}".format(self=self)

        for pair in self.headerCols:
            self.output += fmtHead.format (*pair)

        self.output += lineDivider
        self.output += self.styles.linesep
        self.output += self.styles.colsep_start
        for i in range (len (self.headerFields)):
            fmt = "{{:^{maxBodySize}s}}{colsep}".format(maxBodySize=self.maxBodySize[i], colsep = self.styles.colsep_end)
            self.output += fmt.format (self.headerFields[i])
        self.output += self.styles.linesep
        self.output += lineDivider
        self.output += self.styles.linesep

        for tup in self.bodyRows:
            self.output += self.styles.colsep_start
            fields = []
            for i in range (len (self.maxBodySize)):
                fields            .append (("{:" + tup[i][0] + "" + str (self.maxBodySize[i]) + "s}").format (tup[i][1]))
            self.output += self.styles.colsep_end.join (fields)
            self.output += self.styles.colsep_end + self.styles.linesep
            # self.output += fmtBody.format (*tup)

        self.output += lineDivider
        return self.output

    def appendToHeader (self, name, value=None):
        """Appends entry to header column list, if no value was given
        value from json object by given name will be taken
        """
        value = value if value is not None else self.json[name.lower ().replace (" ", "-")]
        self.headerCols.append ((name, value))

        if self.maxNameSize < len (str (name)):
            self.maxNameSize = len (str (name))

    def appendToBody (self, values):
        """Appends entry to body row list.
        value is tupple of tupples, where inner tupper has two elements, first formatting character, and second value,
        formatting character is used in string format() method
        designating alignment
        < for left
        > for right
        ^ for center
        """
        self.bodyRows.append (values)

        # default empty array
        if self.maxBodySize is None:
            self.maxBodySize = [self.styles.min_width] * len (values)

        # update max length
        for i in range (len (self.maxBodySize)):
            self.maxBodySize[i] = max (self.maxBodySize[i], len (str (values[i][1])))

    def processHeader (self, json):
        """Appends header information"""
        self.appendToHeader ("Program name")
        self.appendToHeader ("Program version")
        self.appendToHeader ("Program branch")
        self.appendToHeader ("Program revision")
        self.appendToHeader ("Program build")
        self.appendToHeader ("Timer resolution")

        if 'source-dir' in json:
            self.appendToHeader ("Source dir")

        desc = re.sub ("\s+", " ", json["task-description"], re.M)
        self.appendToHeader ("Task description", desc)
        self.appendToHeader ("Task size")

        self.appendToHeader ("Run process count")
        self.appendToHeader ("Run started", json["run-started-at"])
        self.appendToHeader ("Run ended", json["run-finished-at"])
        self.appendToHeader ("Run duration", json["run-finished-at"] - json["run-started-at"])

    def processBody (self, json, level):
        """Recursive body processing"""
        if level > 0:
            self.appendToBody ((
                ("<", "{:6.2f} {:s} {:s}".format (json["percent"], self.styles.leading_char * (level - 1) * 1, json["tag"])),
                ("^", "{:d}".format (json["call-count"])),
                ("^", "{:1.4f}".format (json["cumul-time-max"])),
                ("^", "{:1.4f}".format (json["cumul-time-max"] / json["cumul-time-min"])),
                ("^", "{:1.4f}".format (json["cumul-time-sum"] / json["call-count-sum"])),
                ("^", "{:1.4f}".format (json["cumul-time-sum"])),
                ("<", "{:>24s} : {:<5d} {:s}".format (json["function"], json["file-line"], json["file-path"]))
            ))

        try:
            for child in json["children"]:
                self.processBody (child, level + 1)
        except Exception as e:
            pass
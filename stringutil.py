__author__ = 'jan-hybs'


class StringUtil (object):

    @staticmethod
    def join (iterable, prefix="", suffix="", separator=","):
        result = ""
        result += prefix
        result += (suffix+separator+prefix).join (iterable)
        result += suffix

        return result

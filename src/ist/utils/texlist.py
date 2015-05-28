# encoding: utf-8
# author:   Jan Hybs


class texlist (list):
    def __init__ (self, name=''):
        super (list, self).__init__ ()
        self.name = name
        self.counter = 1

    def tag (self, field_name, *values):
        self.append ('\\' + field_name)
        for value in values:
            self.add (value)

        return self

    def KeyItem (self, *args):
        self.tag ('KeyItem', *args)

        return self

    def add (self, value=''):
        self.append ("{" + value + "}")
        return self

    def open (self):
        self.append ('{')
        return self

    def close (self):
        self.append ('}')
        return self

    def hyperB (self, value, n='IT::'):
        self.tag ('hyperB', self.u2d ((n if n.endswith ('::') else n + '::') + value))
        self.add (self.u2s (value))

        return self

    def slash (self, value=''):
        self.append ('\\')
        if value:
            self.append (value)

        return self

    def Alink (self, value, n="IT::"):
        self.tag ('Alink', self.u2d ((n if n.endswith ('::') else n + '::') + value))
        self.add (self.u2s (value))

        return self

    def textlangle (self, value, namespace='\\it '):
        self.slash ('textlangle')
        self.add (namespace + value + ' ')
        self.slash ('textrangle')

        return self

    def newline (self):
        self.append ('\n')
        return self

    def element (self):
        self.counter = 0
        return self

    def open_element (self, name):
        self.tag ('begin', self.name)
        return self

    def close_element (self, name):
        self.tag ('end', name)
        return self

    def __enter__ (self):
        if self.counter == 0:
            self.open_element (self.name)
        else:
            self.open ()
        self.counter += 1
        return self

    def __exit__ (self, exception_type, exception_value, traceback):
        self.counter -= 1
        if self.counter == 0:
            self.close_element (self.name)
        else:
            self.close ()
        return self

    def add_description_field (self, value):
        self.add (self.description (value))

    def description (self, value):
        return value.strip ().replace ('\n', '\\\\').replace ('\\n', '\\\\')

    def u2d (self, value):
        return value.replace ('_', '-')

    def u2s (self, value):
        return value.replace ('_', '\\_')
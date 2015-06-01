# encoding: utf-8
# author:   Jan Hybs
import re


class texlist (list):
    def __init__ (self, name=''):
        super (list, self).__init__ ()
        self.name = name
        self.counter = 1

    def tag (self, field_name, *values):
        self.slash (field_name)
        for value in values:
            self.add_s (value)

        return self

    def KeyItem (self, *args):
        self.tag ('KeyItem', *args)

        return self

    def add (self, value=''):
        self.append ("{" + value + "}")
        return self

    def add_s (self, value=''):
        '''
        Add field with value escaped
        '''
        self.append ("{" + self.escape (value) + "}")
        return self

    def add_d (self, value=''):
        '''
        Add field with value underscores replaced by dashed
        '''
        self.append ("{" + self.secure (value) + "}")
        return self

    def open (self):
        self.append ('{')
        return self

    def close (self):
        self.append ('}')
        return self

    def hyperB (self, value, n='IT::'):
        self.tag ('hyperB', self.secure ((n if n.endswith ('::') else n + '::') + value))
        self.add (self.escape (value))

        return self

    def slash (self, value=''):
        self.append ('\\')
        if value:
            self.append (value)

        return self

    def Alink (self, value, n="IT::"):
        self.tag ('Alink', self.secure ((n if n.endswith ('::') else n + '::') + value))
        self.add (self.escape (value))

        return self

    def AddDoc (self, value):
        self.slash ('AddDoc', self.escape (value))

    def textlangle (self, value, namespace='\\it '):
        self.slash ('textlangle')
        self.add (self.escape (namespace + value + ' ').lower ())
        self.slash ('textrangle')

        return self

    def newline (self):
        self.append ('\n')
        return self

    def element (self):
        self.counter = 0
        return self

    def open_element (self, name):
        self.tag ('begin', name)
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
        return self.escape (value.strip ().replace ('\n', '\\\\'))

    def secure (self, value):
        return value \
            .replace ('_', '-') \
            .replace ('>', '') \
            .replace ('<', '')

    def escape (self, value):
        value = re.sub (r'\$ElementData', r'\$ElementData', value)
        value = value \
            .replace ('_', '\\_') \
            .replace ('->', '$\\rightarrow$') \
            .replace ('<-', '$\\leftarrow$')
        return value
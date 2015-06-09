# encoding: utf-8
# author:   Jan Hybs

import xml.etree.ElementTree as ET


class htmltree(ET):
    def __init__(self, *args, **kwargs):
        super(ET, self).__init__(*args, **kwargs)
        self.root = ET.Element('div')

    def tag(self, tagname, value='', **attributes):
        # self.root.append()
        pass
#!/usr/bin/env python
import re
import glob

class FileReader(object):
    OPTION_LINE_RE = re.compile(r'^#!\s*(.+?)\s*=(.+?)\s*$')

    def __init__(self):
        self.opts = {
            'sep': ' ',
            'cols': 'sum',
        }
    
    def read_option_line(self, l):
        m = self.OPTION_LINE_RE.match(l)
        if not m:
            raise ValueError
        k = m.group(1)
        v = m.group(2)

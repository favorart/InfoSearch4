#!/usr/bin python
# -*- coding: utf-8 -*-

import codecs
import sys
import re


is_word = re.compile(ur'\S')
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for line in sys.stdin:
    splt = line.strip().split('\t', 1)
    if len(splt[0]) > 0 and is_word.match(splt[0]):
        print line

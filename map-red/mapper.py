#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64decode
from zlib import decompress

import codecs
import sys
import re


# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
# Просто зачитываем
for line in sys.stdin:
    print line


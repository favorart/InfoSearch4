#!/usr/bin python
# -*- coding: utf-8 -*-

import codecs
import sys

# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for line in sys.stdin:
    # отсортировано!
    sys.stdout.write(line)


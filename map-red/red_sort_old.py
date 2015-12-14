#!/usr/bin python
# -*- coding: utf-8 -*-

from itertools import groupby
from operator import itemgetter
import codecs
import sys


# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for word, group in groupby((line.strip().split('\t') for line in sys.stdin), itemgetter(0)):

    if  u'$' not in word:
        # Сортируем посчитанную статистику по документам
        docs4word = [ g  for g in group  if len(g) > 1 ]
        docs4word.sort(key=lambda g: int(g[1]))

        for g in docs4word:
            print '\t'.join(g)
    else:
        for g in group:
            print '\t'.join(g)



#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from itertools import groupby
from operator import itemgetter
import codecs
import sys

import zipimport
importer = zipimport.zipimporter('bs123.zip')


if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    # all_docs= povarenok:199456, lenta:564548
    max_number = int(sys.argv[2]) # max(199460, 564550)
    archiver = module.FibonacciArchiver( max_number )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise ValueError


sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for word, group in groupby((line.strip().split('\t', 1) for line in sys.stdin), itemgetter(0)):
    
    ids = []
    for sid, gr in groupby(group.strip().split('\t'), itemgetter(1)):
        pos_s = [ int(g[2]) for g in grp ]
        pos_s.sort()

        for i in xrange(len(pos_s) - 1, 0, -1):
            pos_s[i] -= pos_s[i-1]
        ids.append( (int(sid), pos_s) )

    ids = sorted(ids, key=itemgetter(0))
    for i in xrange(len(ids) - 1, 0, -1):
        ids[i][0] -= ids[i-1][0]

    numbers = []
    for tup in ids:
        numbers.append(tup[0],len(tup[2]))
        numbers += tup[2]

    coded = archiver.code(numbers)
    print u'%s\t%s' % (word, b64encode(coded))


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64decode
import pymorphy2
import codecs
import sys
import os


verbose = False
if verbose:
    if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
        import  fib_archive
        # all_docs= povarenok:199456, lenta:564548
        max_number = int(sys.argv[2]) # max(199460, 564550)
        archiver = module.FibonacciArchiver( max_number )

    elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
        import s9_archive
        archiver =  s9_archive.Simple9Archiver   ()

    else: raise ValueError


if not os.path.exists('data'):
    os.makedirs('data')

dat_name = sys.argv[3] if len(sys.argv) > 3 else './data/reduced.txt'
bin_name = sys.argv[4] if len(sys.argv) > 4 else './data/backward.bin'
ndx_name = sys.argv[5] if len(sys.argv) > 5 else './data/index.txt'

#  2 files:
#  --------
#     + (word  offset  size) concat
#     + bin_archived_(back_index)_concat-ed
with open(bin_name, 'wb') as f_bin:
    with codecs.open(ndx_name, 'w', encoding='utf-8') as f_index:
        with codecs.open(dat_name, 'r', encoding='utf-8') as f_data:
            for line in f_data:
                word, coded = line.strip().split()

                data = b64decode(coded)
                if verbose: print archiver.decode(data)

                print >>f_index, u'%s\t%d\t%d' % (word, f_bin.tell(), len(data))
                f_bin.write(data)


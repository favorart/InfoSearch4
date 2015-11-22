#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from itertools import groupby
from operator import itemgetter
from array import *
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


use_hashes = False

sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
# codecs.open('data/povarenok1000_mapped.txt', 'r', encoding='utf-8')), 
for word, group in groupby((line.strip().split('\t', 1) for line in sys.stdin), itemgetter(0)):

    if  word == u'$':
                
        docs = [ ( int(g[1].split('\t')[0]), int(g[1].split('\t')[1]) ) for g in group ]
        del group

        N = len(docs) # число документов
        Ls = array('i', [0] * (N + 1)) # длины документов

        Ls[0] = N
        for doc_id, doc_len in docs:
            Ls[doc_id + 1] = doc_len
        del docs

        coded = archiver.code(Ls)
        del Ls

        print u'$\t%s' % ( b64encode(coded) )
        del coded

    else:
        ids = []

        for id, new_group in groupby((g[1].strip().split('\t') for g in group), itemgetter(0)):

            if use_hashes:

                tuples = [ (int(g[1]), int(g[2])) for g in new_group ]
                del new_group
                tuples.sort(key=itemgetter(0))

                posits = array('i', [ t[0] for t in tuples])
                hashes = array('i', [ t[1] for t in tuples])
                del tuples

            else:
                posits = [ int(g[1]) for g in new_group ]
                del new_group
                posits.sort()

            # coordinates
            for i in xrange(len(posits) - 1, 0, -1):
                posits[i] -= posits[i-1]
        
            ids.append( array('i', [int(id), len(posits)]) )

            coded_pos = archiver.code(posits); del posits
            if use_hashes:
                coded_hss = archiver.code(hashes); del hashes
                print u'%s\t%s\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos), b64encode(coded_hss))
                del coded_hss
            else:
                print u'%s\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos))
            del coded_pos
            

        ids.sort(key=itemgetter(0))        
        for i in xrange(len(ids) - 1, 0, -1):
            ids[i][0] -= ids[i-1][0]

        # with open('./data/check.txt', 'w') as f:
        #     print >>f, id_s.tolist() + positions.tolist() # ' '.join(ids + positions.tolist())

        ids = [ item for t in ids for item in t ]
        coded_ids = archiver.code(ids)
        del ids

        print u'%s\t%s\t%s' % (word, 0, b64encode(coded_ids))
        del coded_ids


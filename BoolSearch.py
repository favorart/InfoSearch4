#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import codecs
import sys
import re
# import numpy as np

import zipimport
importer = zipimport.zipimporter('bs123.zip')


if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    fib_archive = importer.load_module('fib_archive')
    # all_docs= povarenok:199456, lenta:564548
    max_number = int(sys.argv[2]) # max(199460, 564550)
    archiver = fib_archive.FibonacciArchiver( max_number )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    s9_archive = importer.load_module('s9_archive')
    archiver =  s9_archive.Simple9Archiver   ()

else: raise ValueError


bin_name = sys.argv[3] if len(sys.argv) > 3 else './data/backward.bin'
ndx_name = sys.argv[4] if len(sys.argv) > 4 else './data/index.txt'
ndx_lens = sys.argv[5] if len(sys.argv) > 5 else './data/dlens.txt'
url_name = sys.argv[6] if len(sys.argv) > 6 else 'C:\\Users\\MainUser\\Downloads\\Cloud.mail\\povarenok.ru\\all\\urls.txt'


class BooleanSearch(object):
    """ """
    def __init__(self, ndx_name, bin_name):
        """ """
        self.bin_name = bin_name
        self.ndx_name = ndx_name
        self.w_offsets = {}
        with codecs.open(ndx_name, 'r', encoding='utf-8') as f_index:
            for line in f_index.readlines():
                word, offset, size = line.strip().split()
                self.w_offsets[word] = (offset, size)

    def search(self, query_words, up_positions=False, up_hashes=False):
        """ """
        answer = set()
        oper = ''
    
        with open(self.bin_name, 'rb') as f_backward:
            for q in query_words:
                if   q == 'AND' or q == 'OR'or q == 'NOT':
                    oper = q
                else:
                    # try:
                    if 1:
                        offset, size = self.w_offsets[q.lower()]
                        offset, size = int(offset), int(size)
                    # except:
                    #     print q.lower()
                    #     continue

                    f_backward.seek(offset)
                    coded = f_backward.read(size)
                    decoded = decoder.decode(coded)

                    for i in xrange(1, len(decoded)):
                        decoded[i] += decoded[i-1]

                    # print decoded
                    decoded = set(decoded)

                    if      not answer : answer  = decoded
                    elif oper == 'AND' : answer &= decoded
                    elif oper == 'OR'  : answer |= decoded
                    elif oper == 'NOT' : answer -= decoded
                    else: break

        return list(answer)


if __name__ == '__main__':

    print 'query=',
    if sys.platform.startswith('win'):
        query = unicode(sys.stdin.readline(), 'cp866')
    else:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        query = unicode( sys.stdin.readline() )

    morph = pymorphy2.MorphAnalyzer()
    bs = BooleanSearch(ndx_name,bin_name)
    
    query_words = [ morph.parse(w)[0].normal_form for w in query.split() ]
    # query_words = [ w for w in query_words if len(w) >= 2 ]
    answer = bs.search(query_words)

    urls = []
    with open(url_name, 'r') as f_urls:
        for line in f_urls.readlines():
            id, url = line.strip().split()
            urls.append(url)

    # print answer
    print '\n', '\n'.join([ urls[i] for i in answer ]), '\n'


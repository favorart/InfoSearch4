#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import pymorphy2
import pprint
import codecs
import json
import sys
import re

import zipimport
importer = zipimport.zipimporter('bs123.zip')


class BooleanSearch(object):
    """ """
    def __init__(self, ndx_name, bin_name, archiver):
        """ Constructor:
            word_index = { 'norm' : { 'ids'    : (offset, size),
                                      'lens'   : (offset, size),
                                      'posits' : (offset, size),
                                      'hashes' : (offset, size) }, ... }
        """
        with codecs.open(ndx_name, 'r', encoding='utf-8') as f_index:
            self.word_index = json.loads(f_index.read(), encoding='utf-8')
        # pprint.pprint(self.w_offsets['0'])
        self.bin_name = bin_name
        self.ndx_name = ndx_name
        self.archiver = archiver

    def extract(self, query_norms,
                up=['ids', 'lens', 'posits', 'hashes'],
                decode_posits_and_hashes=False):
        """ Extract data by query words """
        answer = {}

        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:

                try:
                # if 1:
                    dic = self.word_index[norm]
                except:
                    print norm
                    # answer[norm] = None
                    continue

                answer[norm] = {}
                for key in up:

                    offset, size = dic[key]
                    f_backward.seek(offset)
                    coded = f_backward.read(size)

                    if decode_posits_and_hashes or key == 'ids' or key == 'lens':
                        decoded = self.archiver.decode(coded)
                        # print decoded
                        if key == 'ids' or key == 'posits':
                            for i in xrange(1, len(decoded)):
                                decoded[i] += decoded[i-1]
                        answer[norm][key] = decoded
                    else:
                        answer[norm][key] = coded

        return answer

    def search(self, query_norms):
        """ Boolean Search by query """
        oper = ''
        answer = set()
        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:
                if   norm == 'AND' or norm == 'OR'or norm == 'NOT':
                    oper = norm
                else:
                    try:
                    # if 1:
                        offset, size = self.word_index[norm]['ids']
                    except:
                        print norm
                        continue

                    f_backward.seek(offset)
                    coded = f_backward.read(size)
                    decoded = self.archiver.decode(coded)

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


import utils
if __name__ == '__main__':

    args = utils.parse_args()

    if  args.fib:
        fib_archive = importer.load_module('fib_archive')
        archiver = fib_archive.FibonacciArchiver(args.fib)

    elif args.s9:
        s9_archive = importer.load_module('s9_archive')
        archiver =  s9_archive.Simple9Archiver()

    print 'query=',
    if sys.platform.startswith('win'):
        query = unicode(sys.stdin.readline(), 'cp866')
    else:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        query = unicode( sys.stdin.readline() )
    
    morph = pymorphy2.MorphAnalyzer()
    bs = BooleanSearch(ndx_name, bin_name)
    
    query_norms = [ morph.parse( w.lower() )[0].normal_form 
                    for w in query.split()
                    if  w not in ['AND', 'OR', 'NOT']
                  ]

    answer = bs.search(query_norms)

    with open(args.url_name, 'r') as f_urls:
        urls = map(lambda line: line.strip().split(), f_urls)

    # print answer
    print '\n', '\n'.join([ urls[i] for i in answer ]), '\n'

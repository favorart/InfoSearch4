#!/usr/bin python
# -*- coding: utf-8 -*-

from collections import defaultdict
from base64 import b64decode, b64encode
from operator import itemgetter

import pymorphy2
# import pprint
import pickle
import codecs
import time
# import ijson
import json
import sys
sys.path.insert(0, 'map-red')

import re
import os

import utils
import s9_archive
import fib_archive


class BooleanSearch(object):
    """ """
    def __init__(self, ndx_name, bin_name, archiver):
        """ Constructor:
            word_index = { 'norm' : { 'ids'    : (offset, size),
                                      'lens'   : (offset, size),
                                      'posits' : (offset, size),
                                      'hashes' : (offset, size) }, ... }
        """
        self.word_index = {}

        if not os.path.exists(ndx_name + '.pkl'):
            with codecs.open(ndx_name, 'r', encoding='utf-8') as f_index:
                self.word_index = json.load(f_index, encoding='utf-8')
                
            with open(ndx_name + '.pkl', 'w') as f_index:
                pickle.dump(self.word_index, f_index)
        else:
            with open(ndx_name + '.pkl', 'r') as f_index:
                self.word_index = pickle.load(f_index)

        self.bin_name = bin_name
        self.ndx_name = ndx_name
        self.archiver = archiver

        # Caching or not the bin-read-index of word
        self.index_size2cache = 30000
        self.cache_max_len = 100
        self.fn_cache = bin_name + '-cache-json.txt'
        # cache: { word: (index, time) }

        try:
            if  os.path.exists(self.fn_cache):
                with codecs.open(self.fn_cache, 'r', encoding='utf-8') as f_cache:
                    self.cache = json.load(f_cache,  encoding='utf-8')
        except:
            self.cache = {}
            
    def decode_posits_and_hashes_for_doc(self, index, doc_index):
        """ """
        posits, coded = index['posits']
        coded = b64decode(coded)

        if doc_index >= len(posits):
            print doc_index

        b,e = posits[doc_index], posits[doc_index + 1]
        decoded_posits = self.archiver.decode(coded[b:b+e])
        
        for i in xrange(1, len(decoded_posits)):
            decoded_posits[i] += decoded_posits[i-1]
        # ---------------------------------------------------
        hashes, coded = index['hashes']
        coded = b64decode(coded)

        b,e = hashes[doc_index], hashes[doc_index + 1]
        decoded_hashes = self.archiver.decode(coded[b:b+e])
        # ---------------------------------------------------
        return  (decoded_posits, decoded_hashes)

    def read_and_decode_word_index(self, f_backward, norm, dic, up):
        """ """
        index = {}
        for key in up:

            if  key == 'ids' or key == 'lens':

                if len(dic[key]) == 2:
                    offset,  size  = dic[key]
                    offset1, size1 = 0, 0
                else:
                    offset,  size, \
                    offset1, size1 = dic[key]

                f_backward.seek(offset)
                coded = f_backward.read(size)

                decoded = self.archiver.decode(coded)
                # print decoded
                if key == 'ids':
                    for i in xrange(1, len(decoded)):
                        decoded[i] += decoded[i-1]

                if  size1:
                    f_backward.seek(offset1)
                    coded1 = f_backward.read(size1)

                    decoded1 = self.archiver.decode(coded1)
                    # print decoded
                    if key == 'ids':
                        for i in xrange(1, len(decoded1)):
                            decoded1[i] += decoded1[i-1]
                else: decoded1 = []
                index[key] = decoded + decoded1

                # print key, len(index[key])

            else:
                offset, data = dic[key]
                sizes = self.archiver.decode( b64decode(data) )
                # print decoded
                size = sum(sizes)

                f_backward.seek(offset)
                coded = f_backward.read(size)

                index[key] = ([0] + sizes, b64encode(coded) )

                # print key, len(index[key][0])

        return  index

    def extract(self, query_norms,
                up=['ids', 'lens', 'posits', 'hashes'],
                verbose=False):
        """ Extract all data by query words """
        query_index = {}
        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:

                if  norm in self.cache:
                    query_index[norm] = self.cache[norm]['index']
                    self.cache[norm]['time'] = time.time()
                    continue
    
                if  norm not in self.word_index:
                    if verbose: utils.print_utf('--- ' + norm)
                    continue
  
                # start_time = time.time()
                query_index[norm] = self.read_and_decode_word_index(f_backward, norm, 
                                                                    self.word_index[norm], up=up)
                # if verbose: print "arc. %.3f sec." % (time.time() - start_time),
                self.cache_insert(norm, query_index[norm])
        # if verbose: print 'cache_len %d' % len(self.cache)
        return query_index

    def search(self, query_norms, verbose=False):
        """ Boolean Search by query """
        oper = ''
        query_index = set()

        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:

                if  norm in ['AND', 'OR', 'NOT']:
                    oper = norm

                else:
                    try: # if 1:

                        # TODO: !!!
                        offset, size = self.word_index[norm]['ids']
                        # offset, size = self.w_offsets[norm]
                    except:
                        if verbose: utils.print_utf('--- ' + norm)
                        continue

                    f_backward.seek(offset)
                    coded = f_backward.read(size)
                    decoded = self.archiver.decode(coded)

                    for i in xrange(1, len(decoded)):
                        decoded[i] += decoded[i-1]

                    # print decoded
                    decoded = set(decoded)

                    if not query_index : query_index  = decoded
                    elif oper == 'AND' : query_index &= decoded
                    elif oper == 'OR'  : query_index |= decoded
                    elif oper == 'NOT' : query_index -= decoded
                    else: break

        return list(query_index)

    def cache_insert(self, norm, index):
        """ """
        if  len(self.cache) >= self.cache_max_len:
            part = int(float(self.cache_max_len) / 3)

            items = self.cache.items()
            items.sort(key=lambda x: x[1]['time'], reverse=True)
            self.cache = dict(items[:part])

            with codecs.open(self.fn_cache, 'w', encoding='utf-8') as f_cache:
                str = json.dumps(self.cache, ensure_ascii=False, encoding='utf-8')
                f_cache.write(str)

        # if (time.time() - start_time) > self.time2cache:
        elif len(index['ids']) >= self.index_size2cache:

            self.cache[norm] = { 'index' : index, 'time' : time.time() }

            with codecs.open(self.fn_cache, 'w', encoding='utf-8') as f_cache:
                json.dump(self.cache, f_cache, ensure_ascii=False, encoding='utf-8')


if __name__ == '__main__':

    args = utils.parse_args()

    if  args.fib:
        archiver = fib_archive.FibonacciArchiver(args.fib)
    elif args.s9:
        archiver =  s9_archive.Simple9Archiver()

    morph = pymorphy2.MorphAnalyzer()
    bs = BooleanSearch(args.ndx_name, args.bin_name, archiver)

    with open(args.url_name, 'r') as f_urls:
        urls = map(lambda line: utils.norm_url(line.split()[1]), f_urls)

    if not args.mrk_name:

        while True:

            print 'query=',
            if sys.platform.startswith('win'):
                query = unicode(sys.stdin.readline(), 'cp866')
            else:
                reload(sys)
                sys.setdefaultencoding('utf-8')
                query = unicode( sys.stdin.readline() )
            
            if u'exit' in query: break

            query_norms = [  morph.parse( w.lower() )[0].normal_form 
                    for w in query.split()
                    if  w not in ['AND', 'OR', 'NOT']  ]

            answer = bs.search(query_norms)
            # print answer
            print '\n', '\n'.join([ urls[i] for i in answer ]), '\n'

    else:
        found = 0
        with codecs.open(args.mrk_name, 'r', encoding='utf-8') as f_marks:
            for i, line in enumerate(f_marks):

                if not (i%10): print ">>> ", i
                splt = line.strip().split('\t')
                if len(splt) > 1:
                    query, mark_url = splt[0], utils.norm_url(splt[1])

                    query_norms = [ morph.parse( w.lower() )[0].normal_form  for w in query.split()  if len >= 2 ]
                    query_norms = u' AND '.join(query_norms).split()
                    answer = bs.search(query_norms)

                    urls_ans = '|'.join([ urls[i]  for i in answer  if i < len(urls) ])
                    if re.match(urls_ans, mark_url):
                        print query.encode('cp866', 'ignore')
                        found += 1
        print '\n\n', found
#!/usr/bin python
# -*- coding: utf-8 -*-

from collections import defaultdict
from base64 import b64decode, b64encode
from operator import itemgetter

import pymorphy2
# import pprint
import codecs
import time
import json
import sys
sys.path.insert(0, 'map-red')

import re

import utils
import s9_archive
import fib_archive


class BooleanSearch(object):
    """ """
    def __init__(self, ndx_name, bin_name, archiver, use_json=True):
        """ Constructor:
            word_index = { 'norm' : { 'ids'    : (offset, size),
                                      'lens'   : (offset, size),
                                      'posits' : (offset, size),
                                      'hashes' : (offset, size) }, ... }
        """
        self.word_index = {}
        with codecs.open(ndx_name, 'r', encoding='utf-8') as f_index:
            if use_json:
                self.word_index = json.loads(f_index.read(), encoding='utf-8')
            else:
                for line in f_index:
                    splt = line.strip().split('\t')
                    if len(splt) == 2:
                        index = splt[1].split(' ')
                        dic = {}
                        for item in index:
                            value = item.split(',')
                            dic[value[0]]= value[1] if len(value) < 3 else map(int, value[1:])
                        self.word_index[splt[0]] = dic

        # # USING THE OLD INDEX
        # self.w_offsets = {}
        # with codecs.open(ndx_name, 'r', encoding='utf-8') as f_index:
        #     for line in f_index.readlines():
        #         word, offset, size = line.strip().split()
        #         self.w_offsets[word] = (int(offset), int(size))

        self.bin_name = bin_name
        self.ndx_name = ndx_name
        self.archiver = archiver

        # Performance time to define
        # caching or not the bin-read-index of word
        self.time2cache=20. # in seconds
        self.cache_max_len = 100
        self.cache = {}

    def decode_posits_and_hashes_for_doc(self, index, doc_index):
        """ """
        posits, coded = index['posits']

        b,e = posits[doc_index], posits[doc_index + 1]
        decoded_posits = self.archiver.decode(coded[b:b+e])
        
        for i in xrange(1, len(decoded_posits)):
            decoded_posits[i] += decoded_posits[i-1]
        # ---------------------------------------------------
        hashes, coded = index['hashes']

        b,e = hashes[doc_index], hashes[doc_index + 1]
        decoded_hashes = self.archiver.decode(coded[b:b+e])
        # ---------------------------------------------------
        return  (decoded_posits, decoded_hashes)

    def extract(self, query_norms,
                up=['ids', 'lens', 'posits', 'hashes'],
                verbose=False):
        """ Extract all data by query words """
        answer = {}

        if  len(self.cache) >= self.cache_max_len:
            half = self.cache_max_len / 2
            items = self.cache.items()
            items.sort(key=lambda x: x[1][1], reverse=True)
            self.cache = dict(items[:half])

        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:

                if  norm in self.cache:
                    answer[norm] = self.cache[norm][0]
                    self.cache[norm][1] = time.time()
                    continue
    
                if  norm not in self.word_index:
                    if verbose:
                        if sys.platform.startswith('win'):
                            print '---', norm.encode('cp866', 'ignore')
                        else:
                            print '---', norm
                    continue

                dic = self.word_index[norm]
                    
                start_time = time.time()

                answer[norm] = {}
                for key in up:

                    if  key == 'ids' or key == 'lens':
                        offset, size = dic[key]
                        f_backward.seek(offset)
                        coded = f_backward.read(size)

                        decoded = self.archiver.decode(coded)
                        # print decoded

                        if key == 'ids':
                            for i in xrange(1, len(decoded)):
                                decoded[i] += decoded[i-1]
                        answer[norm][key] = decoded

                    else:
                        offset, data = dic[key]
                        sizes = self.archiver.decode( b64decode(data) )
                        # print decoded
                        size = sum(sizes)

                        f_backward.seek(offset)
                        coded = f_backward.read(size)

                        answer[norm][key] = ([0] + sizes, coded)

                if (time.time() - start_time) > self.time2cache:
                    # if verbose: print "arc. %.3f sec." % (time.time() - start_time),
                    self.cache[norm] = [ answer[norm], time.time() ]
        # if verbose: print 'cach. %d' % len(self.cache)
        return answer

    def search(self, query_norms, verbose=False):
        """ Boolean Search by query """
        oper = ''
        answer = set()

        with open(self.bin_name, 'rb') as f_backward:
            for norm in query_norms:

                if  norm in ['AND', 'OR', 'NOT']:
                    oper = norm

                else:

                    try:
                    # if 1:
                        offset, size = self.word_index[norm]['ids']
                        # offset, size = self.w_offsets[norm]
                    except:
                        if verbose:
                            if sys.platform.startswith('win'):
                                print '---', norm.encode('cp866', 'ignore')
                            else:
                                print'---', norm
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
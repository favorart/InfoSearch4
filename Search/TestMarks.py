#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import sys
import re

import utils
from BoolSearch import BooleanSearch
from BlackSearch import BlackSearch
from TextSearch import TextSearch
# from reshape import reshape


if __name__ == '__main__':

    args = utils.parse_args()

    if  args.fib:
        fib_archive = importer.load_module('fib_archive')
        archiver = fib_archive.FibonacciArchiver(args.fib)

    elif args.s9:
        s9_archive = importer.load_module('s9_archive')
        archiver = s9_archive.Simple9Archiver()

    with open(args.url_name, 'r') as f_urls:
        urls = map(lambda line: utils.norm_url(line.strip().split()[1]), f_urls)
        
    bs = BooleanSearch(args.ndx_name, args.bin_name, archiver)     
    br = BlackSearch(bs, lex=utils.MyLex(), dlen_name=args.len_name)
    ts = TextSearch(br)

    found = []
    with codecs.open(args.mrk_name, 'r', encoding='utf-8') as f_marks:
        for i,line in enumerate(f_marks.readlines()[10:]):
            splt = line.split('\t')
            if len(splt) != 2: continue

            query, mark_url = splt[0], utils.norm_url(splt[1])

            answer = ts.search(query, 1000)
            if answer:
                # m = re.search(mark_url, ' '.join([ urls[i] for i in answer ]))
                # if m is not None:
                found_urls = [ urls[i[0]] for i in answer ]
                if  mark_url in found_urls:
                    index = found_urls.index(mark_url)
                    print (mark_url + ' ' + url)
                    found.append(index)
                    break
                # else: print '\t' + query.encode('cp866', 'ignore')


    # urls = []
    # with open(url_name, 'r') as f_urls:
    #     for line in f_urls.readlines():
    #         id, url = line.strip().split()
    #         url = re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', url)
    #         urls.append(url)
    # 
    # found = 0
    # bs = BooleanSearch(ndx_name, bin_name)
    # with codecs.open(mrk_name, 'r', encoding='utf-8') as f_marks:
    #     for line in f_marks:
    #         splt = line.split('\t')
    #         if len(splt) == 2:
    #             query, mark_url = splt
    #             mark_url = re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', mark_url)
    # 
    #             query_words = ' AND '.join([ w for w in query.split() if len(w) > 2 ]).split()
    #             answer = bs.search(query_words)
    #             
    #             m = re.search(mark_url, ' '.join([ urls[i] for i in answer ]))
    #             if m is not None:
    #                 print (mark_url + ' ' + url)
    #                 found += 1
    #                 break
    #             # else: print '\t' +
    print found


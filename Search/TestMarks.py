#!/usr/bin python
# -*- coding: utf-8 -*-

import codecs
import time
import sys
sys.path.insert(0, 'archive')

import re
import os

import utils
from BoolSearch import BooleanSearch
from BlackSearch import BlackSearch
from TextSearch import TextSearch

import s9_archive
import fib_archive


if __name__ == '__main__':

    args = utils.parse_args()

    if  args.fib:
        archiver = fib_archive.FibonacciArchiver(args.fib)
    elif args.s9:
        archiver =  s9_archive.Simple9Archiver()

    if  not os.path.exists(args.url_name + 'urls.txt'):
        with open(args.url_name, 'r') as f_urls:
            urls = map(lambda line: utils.norm_url(line.strip().split()[1]), f_urls)

        with open(args.url_name + 'urls.txt', 'w') as f:
            print >>f, '\n'.join(urls)
    else:
        with open(args.url_name + 'urls.txt', 'r') as f:
            urls = f.read().split('\n')
        
    bs = BooleanSearch(args.ndx_name, args.bin_name, archiver)     
    br = BlackSearch(bs, lex=utils.MyLex(), dlen_name=args.len_name)
    ts = TextSearch(br)

    IS_IN = 0

    found = []
    with codecs.open(args.rnk_name, 'w', encoding='utf-8') as f_ranks:
        with codecs.open(args.mrk_name, 'r', encoding='utf-8') as f_marks:

            total_time = time.time()
            for i,line in enumerate(f_marks):

                splt = line.split('\t')
                if len(splt) != 2: continue

                query, mark_url = splt[0], utils.norm_url(splt[1])

                print "'%s'" % query
                print >>f_ranks, "'%s'" % query
                inv_q = ts.br.lex.incorrect_keyboard_layout(query)
                if inv_q:
                    print "'%s'" % query
                    print >>f_ranks, "'%s'" % query

                start_time = time.time()
                answer = ts.search(query, 1000)
                print "%.3f sec." % (time.time() - start_time)
                print >>f_ranks, "%.3f sec.\n" % (time.time() - start_time)

                found_urls = '\n'.join([ urls[i] for i in answer ])
                print >>f_ranks, '=', mark_url, '\n', found_urls
                
                if  mark_url in found_urls:
                    print >>f_ranks, 'OK'
                    IS_IN += 1
                else:
                    print '---'
                    print >>f_ranks, '---\n\n'

            print >>f_ranks, "\n%.3f sec.\n" % (time.time() - total_time)
            print >>f_ranks, "IS_IN %d" % IS_IN

    print found


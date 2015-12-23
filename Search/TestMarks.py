#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64decode, b64encode

import codecs
import time
import sys
sys.path.insert(0, 'map-red')

import re
import os

import utils
from BoolSearch import BooleanSearch
from BlackSearch import BlackSearch
from TextSearch import TextSearch

import s9_archive
import fib_archive


def main():
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
    iter = 0

    f_ranks = codecs.open(args.rnk_name, 'w', encoding='utf-8')
    
    with codecs.open('mark_ids.txt', 'r', encoding='utf-8') as f_marks: # args.mrk_name
        with codecs.open('params.txt', 'w', encoding='utf-8') as f_params:

            # L_marks = f_marks.readlines()
            # ts.params = [ p / len(L_marks) for p in ts.params ]
            # print ts.params

            total_time = time.time()
            for it,line in enumerate(f_marks): # L_marks):

                splt = line.split('\t')
                if len(splt) != 2: continue

                # query, mark_url = splt[0], utils.norm_url(splt[1])
                query, mark_id = splt[0], int(splt[1])

                print "%3d '%s'" % (it, query.encode('cp866', 'ignore')),
                print >>f_ranks, "%3d '%s'" % (it, query)

                inv_q = ts.br.lex.incorrect_keyboard_layout(query)
                if inv_q:
                    print "\n    '%s'" % inv_q,
                    print >>f_ranks, "'%s'" % inv_q

                start_time = time.time()
                answer = ts.search(query, 1000, mark_id=mark_id, f_params=f_params)
                print "\t%.3f sec." % (time.time() - start_time),
                print >>f_ranks, "%.3f sec.\n" % (time.time() - start_time)

                # answer_urls = [ urls[i] for i in answer ]
                # found_urls = '\n'.join(answer_urls)
                # print >>f_ranks, mark_id, '=', ','.join([str(a) for a in answer])

                try:
                    z = answer.index(mark_id)
                    print '\tOK(%d)' % z
                    print >>f_ranks, '\tOK(%d)' % z
                    IS_IN += 1
                except:
                    print '\t---'
                    print >>f_ranks, '---\n\n'

            print "\n%.3f sec." % (time.time() - total_time)
            print >>f_ranks, "\n%.3f sec.\n" % (time.time() - total_time)

            print "IS_IN %d" % IS_IN
            print >>f_ranks, "IS_IN %d" % IS_IN

            # iter += 1
            # if  not (iter % 100):
            #     # dump to disk
            #     f_ranks.close()
            #     f_ranks = codecs.open(args.rnk_name, 'a', encoding='utf-8')
        # print ts.params
        # print found



# блюда из кальмаров рецепты                 71447 78.056 sec.     OK (100)
# блюда из кабачков рецепт с фото           170227 66.458 sec.     OK (127)
# шаурма классическая рецепт                 37690 19.114 sec.     OK (11)
# торт                                       87734 18.032 sec.     OK (37)
# салат из соленой красной рыбы             143545 70.659 sec.     OK (209)
# рецепт вкусного тирамису                  187485 22.311 sec.     OK (954)
# салат из курицы с корнем сельдерея         31948 52.520 sec.     OK (225)
# что можно кушать во время великого поста   44327  8.975 sec.     OK (4)
# перчик фаршированный рецепт                93101 20.099 sec.     OK (230)
# жаркое из свинины                         188710 18.819 sec.     OK (273)


# import cProfile, pstats
if  __name__ == '__main__':
   
    # pr = cProfile.Profile()
    # pr.enable()
    # # ... do something ...
    main()

    # pr.disable()
    # 
    # f = codecs.open('profile', 'a', 'utf-8')
    # sortby = 'cumulative'
    # pstats.Stats(pr, stream=f).strip_dirs().sort_stats(sortby).print_stats()
    # f.close()

    # print s.getvalue()
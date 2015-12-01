#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64encode

from itertools import groupby
from operator import itemgetter

import codecs
import sys

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# Выбор архиватора
if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    # povarenok:199456
    archiver = module.FibonacciArchiver( int(sys.argv[2]) )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise Exception("Have NO archiver-argument")


# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for word, group in groupby((line.strip().split('\t', 1) for line in sys.stdin), itemgetter(0)):

    if  u'$' in word:
                
        # Собираем посчитанные длины документов
        Ls = [ ( int(g[1].split('\t')[0]), int(g[1].split('\t')[1]) ) for g in group ]
        # Ls: (doc_id, doc_len)
        Ls.sort(key=itemgetter(0))
        ids, lens = zip(*Ls)

        ids, lens = list(ids), list(lens)
        # уточнаяем номера документов
        if  len(ids) > 1:
            for i in xrange(len(ids) - 1, 0, -1):
                ids[i] -= ids[i-1]

        # всё архивируем вместе
        to_code = [ len(ids) ] + ids + lens
        coded = archiver.code(to_code)
        # сразу отправляем, забываем
        print u'$\t%s' % ( b64encode(coded) )
        del to_code, coded

    else:
        ids_and_pos_lens = []
        # Для каждого слова собираем документы и число вхождений
        for id, new_group in groupby((g[1].strip().split('\t') for g in group), itemgetter(0)):

            # Собираем позиции и хэши
            posits_and_hashes = [ (int(g[1]), int(g[2])) for g in new_group  if len(g) >= 3 ]
            
            posits_and_hashes.sort(key=itemgetter(0))
            posits, hashes = zip(*posits_and_hashes)
            del posits_and_hashes

            posits, hashes = list(posits), list(hashes)
            # coordinates - лучше упаковывем
            if len(posits) > 1:
                for i in xrange(len(posits) - 1, 0, -1):
                    posits[i] -= posits[i-1]
        
            # cобираем документ для этого слова
            ids_and_pos_lens.append( (int(id), len(posits)) )

            # архивируем и отправляем
            coded_pos = archiver.code(posits)
            coded_hss = archiver.code(hashes)
            del posits, hashes
                
            print u'%s\t%06d\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos), b64encode(coded_hss))
            del coded_pos, coded_hss

        # Упаковываем номера документов и соответственные им длины
        ids_and_pos_lens.sort(key=itemgetter(0))
        ids, len_posits = zip(*ids_and_pos_lens)
        del ids_and_pos_lens
        
        ids, len_posits = list(ids), list(len_posits)
        if  len(ids) > 1:
            # document ids shifting
            for i in xrange(len(ids) - 1, 0, -1):
                ids[i] -= ids[i-1]

        # Архивируем их
        coded_ids  = archiver.code(ids)
        coded_lens = archiver.code(len_posits)
        del ids, len_posits

        # И отправляем
        print u'%s\t%06d\t%s\t%s' % (word, 0, b64encode(coded_ids), b64encode(coded_lens))
        del coded_ids, coded_lens


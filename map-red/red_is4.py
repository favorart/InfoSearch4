#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64encode
from itertools import groupby
from operator import itemgetter
from array import *
import codecs
import sys

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# Выбор архиватора
if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    # all_docs= povarenok:199456, lenta:564548
    archiver = module.FibonacciArchiver( int(sys.argv[2]) )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise ValueError


# Флаг - добавляем ли хэши в фильный индекс
if   (len(sys.argv) > 3 and sys.argv[3] == '-e'):
    use_hashes = True
else:
    use_hashes = False


# Длины документов
Ls = []
# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for word, group in groupby((line.strip().split('\t', 1) for line in sys.stdin), itemgetter(0)):

    if  word == u'$':
                
        # Собираем посчитанные длины документов
        # doc_id, doc_len
        docs = [ ( int(g[1].split('\t')[0]), int(g[1].split('\t')[1]) ) for g in group ]
        del group
                
        Ls += docs

    else:
        ids_and_pos_lens = []

        # Для каждого слова собираем документы и число вхождений
        for id, new_group in groupby((g[1].strip().split('\t') for g in group  if len(g) > 1), itemgetter(0)):

            # Для каждого документа у заданного слова
            if use_hashes:

                # Собираем позиции и хэши
                posits_and_hashes = [ (int(g[1]), int(g[2])) for g in new_group  if len(g) >= 3 ]
                del new_group

                if not len(posits_and_hashes): continue

                posits_and_hashes.sort(key=itemgetter(0))
                posits, hashes = zip(*posits_and_hashes)
                del posits_and_hashes

            else:
                # Или просто позиции вместе
                posits = [ int(g[1]) for g in new_group  if len(g) >= 2 ]
                del new_group
                posits.sort()

            # coordinates - лучше упаковывем
            posits = list(posits)
            if len(posits) > 1:
                for i in xrange(len(posits) - 1, 0, -1):
                    posits[i] -= posits[i-1]
        
            # cобираем документ для этого слова
            ids_and_pos_lens.append( (int(id), len(posits)) )

            # архивируем и отправляем
            coded_pos = archiver.code(posits)
            del posits

            if use_hashes:
                coded_hss = archiver.code(hashes)
                del hashes
                
                print u'%s\t%s\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos), b64encode(coded_hss))
                del coded_hss
            else:
                print u'%s\t%s\t%s'     % (word, (int(id) + 1), b64encode(coded_pos))

            del coded_pos

        # Упаковываем номера документов и соответственные им длины
        ids_and_pos_lens.sort(key=itemgetter(0))
        if not ids_and_pos_lens: continue
        ids, len_posits = zip(*ids_and_pos_lens)
        del ids_and_pos_lens
        
        ids = list(ids)
        if  len(ids) > 1:
            # document ids shifting
            for i in xrange(len(ids) - 1, 0, -1):
                ids[i] -= ids[i-1]

        # Архивируем их
        coded_ids  = archiver.code(ids)
        coded_lens = archiver.code(len_posits)
        del ids, len_posits
        # И отправляем
        print u'%s\t%s\t%s\t%s' % (word, 0, b64encode(coded_ids), b64encode(coded_lens))
        del coded_ids, coded_lens


# В конце отправляем глобальную статистику
if Ls:
    Ls.sort(key=itemgetter(0))
    ids, lens = zip(*Ls)
    del Ls

    # Пришлось сделать так, т.к. сортирователь hadoop
    # Не захотел собирать все $$$ в одну кучу для
    # groupby, а распихивал рандомно

    ids = list(ids)
    if  len(ids) > 1:
        for i in xrange(len(ids) - 1, 0, -1):
            ids[i] -= ids[i-1]

    to_code = [ len(ids) ] + ids + list(lens)
    del ids, lens

    coded = archiver.code(to_code)
    del to_code
    print u'$\t%s' % ( b64encode(coded) )
    del coded


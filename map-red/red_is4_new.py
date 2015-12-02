#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64encode
from itertools import groupby
from operator import itemgetter

import array
import codecs
import sys
import time

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# Выбор архиватора
if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    # povarenok: 199456
    archiver = module.FibonacciArchiver( int(sys.argv[2]) )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise Exception("Have NO archiver-argument")


def inserting_sort(arr, sub, new, val):
    """ arr - array.array('i') # posits | ids
        sub - array.array('i') # lens
        new - string
        val - string
    """
    new = int(new)
    
    accum = 0
    for i in xrange(len(arr)):                   
        if (accum + arr[i]) > new:
            next = arr[i]
            arr.remove(next)
            # Уточняем координаты
            next = ((accum + next) - new)
            this = ( new - accum )

            arr.insert(i, next)
            arr.insert(i, this)
            
            sub.insert(i, int(val))
            break
        accum += arr[i]
    else:
        arr.append(new - accum)
        sub.append(int(val))
    return  (arr, sub)


# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for word, group in groupby((line.strip().split('\t', 1) for line in sys.stdin), itemgetter(0)):

    if  u'$' in word:
                
        # Собираем посчитанные длины документов
        Ls = [ ( int(g[1].split('\t')[0]), int(g[1].split('\t')[1]) ) for g in group ]
        del group

        # Ls: (doc_id, doc_len)
        Ls.sort(key=itemgetter(0))
        ids, lens = zip(*Ls)
        del Ls

        ids, lens = list(ids), list(lens)
        # уточнаяем номера документов
        if  len(ids) > 1:
            for i in xrange(len(ids) - 1, 0, -1):
                ids[i] -= ids[i-1]

        # всё архивируем вместе
        to_code = [ len(ids) ] + ids + lens
        del ids, lens

        coded = archiver.code(to_code)
        del to_code
        # сразу отправляем, забываем
        print u'$\t%s' % ( b64encode(coded) )
        del coded

    else:
        ids        = array.array('i', [])
        len_posits = array.array('i', [])
        # Для каждого слова собираем документы и число вхождений
        for id, new_group in groupby((g[1].strip().split('\t') for g in group), itemgetter(0)):

            # Собираем позиции и хэши
            posits = array.array('i', [])
            hashes = array.array('i', [])

            for g in new_group:
                if  len(g) >= 3:
                    g_id, g_posit, g_hash = g
                    # сортировка вставками
                    posits, hashes = inserting_sort(posits, hashes, g_posit, g_hash)

            len_cur_posits = len(posits)
            if  len_cur_posits != len(hashes):
                print >>sys.stderr, word, id, 'posits_len', len(posits), len(hashes)

            # архивируем и отправляем
            if  len_cur_posits > 0:
                coded_pos = archiver.code(posits)
                del posits
                coded_hss = archiver.code(hashes)
                del hashes
            else:
                print >>sys.stderr, word, id, 'posits_len', len(posits), len(hashes)
                del posits, hashes
                continue
        
            # Собираем документ для этого слова
            ids, len_posits = inserting_sort(ids, len_posits, id, len_cur_posits)

            if  len(ids) > 0:
                print u'%s\t%06d\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos), b64encode(coded_hss))
                del coded_pos, coded_hss
            else:
                print >>sys.stderr, word, 'ids_len', len(ids)
                continue

        # Архивируем номера документов и количества позиций
        if  len(ids) > 0:
            coded_ids  = archiver.code(ids)
            del ids
            coded_lens = archiver.code(len_posits)
            del len_posits
        else:
            print >>sys.stderr, word, 'ids_len', len(ids)
            del ids, len_posits
            continue

        # И, наконец, отправляем
        print u'%s\t%06d\t%s\t%s' % (word, 0, b64encode(coded_ids), b64encode(coded_lens))
        del coded_ids, coded_lens


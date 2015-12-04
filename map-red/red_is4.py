#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64encode
from operator import itemgetter

import array
import codecs
import sys

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# -----------------------------------------------------------
# Выбор архиватора
if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    # povarenok:199456
    archiver = module.FibonacciArchiver( int(sys.argv[2]) )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise Exception("Have NO archiver-argument")


# -----------------------------------------------------------
NON_WORD_CHAR = u'$'
def send_lens (Ls):
    """ """
    if  len(Ls) < 1:
        print >>sys.stderr, "NO doc_ids and lens"
        return False

    #  Ls: (doc_id, doc_len)
    Ls.sort(key=itemgetter(0))
    ids, lens = zip(*Ls)
    del Ls

    # уточнаяем номера документов
    if  len(ids) > 1:
        ids = list(ids)
        for i in xrange(len(ids) - 1, 0, -1):
            ids[i] -= ids[i-1]

    # всё архивируем вместе
    to_code = [ len(ids) ] + list(ids) + list(lens)
    del ids, lens
    coded = archiver.code(to_code)
    del to_code
    # сразу отправляем, забываем
    print u'%s\t%s' % ( NON_WORD_CHAR, b64encode(coded) )
    del coded
    return True

# -----------------------------------------------------------
def send_doc_ids_and_lens  (word, ids_and_posit_lens):
    """ """
    if  len(ids_and_posit_lens) < 1:
        print >>sys.stderr, word, 'ids:', \
                 len(ids_and_posit_lens)
        return False

    # Упаковываем номера документов и соответственные им длины
    ids_and_posit_lens.sort(key=itemgetter(0))
    ids, len_posits = zip(*ids_and_posit_lens)
    del ids_and_posit_lens
        
    if  len(ids) > 1:
        ids = list(ids)
        # document ids shifting
        for i in xrange(len(ids) - 1, 0, -1):
            ids[i] -= ids[i-1]

    # Архивируем их
    coded_ids  = archiver.code(ids)
    del ids
    coded_lens = archiver.code(len_posits)
    del len_posits

    # И отправляем
    print u'%s\t%06d\t%s\t%s' % (word, 0, b64encode(coded_ids), b64encode(coded_lens))
    del coded_ids, coded_lens
    return True

# -----------------------------------------------------------
def send_posits_and_hashes (word, id, posits_and_hashes):
    """ """
    if  len(posits_and_hashes) < 1:
        print >>sys.stderr, word, id, \
              'posits and hashes:', \
              len(posits_and_hashes)
        return False

    posits_and_hashes.sort(key=itemgetter(0))
    posits, hashes = zip(*posits_and_hashes)
    del posits_and_hashes

    # coordinates - лучше упаковывем
    if  len(posits) > 1:
        posits = list(posits)
        for i in xrange(len(posits) - 1, 0, -1):
            posits[i] -= posits[i-1]

    # архивируем
    coded_pos = archiver.code(posits)
    del posits
    coded_hss = archiver.code(hashes)
    del hashes
    # и отправляем          
    print u'%s\t%06d\t%s\t%s' % (word, (int(id) + 1), b64encode(coded_pos), b64encode(coded_hss))
    del coded_pos, coded_hss
    # success
    return True

# -----------------------------------------------------------
# State
prev_word = None
prev_w_id = None

Ls = []

ids_and_posit_lens = []
posits_and_hashes  = []


# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

# -----------------------------------------------------------
for line in sys.stdin:

    splt = line.strip().split('\t')
    word = splt[0]

    # -----------------------------------------------------------
    if  prev_word and (word != prev_word):

        if  NON_WORD_CHAR in prev_word:
            send_lens(Ls);  Ls = []

        else:
            len_ph = len(posits_and_hashes)
            success = send_posits_and_hashes(prev_word, prev_w_id, posits_and_hashes)
            posits_and_hashes  = []

            # -----------------------------------------------------------
            if  success:
                # Для каждого слова собираем документы и число вхождений
                ids_and_posit_lens.append( (int(prev_w_id), len_ph) )
                
                send_doc_ids_and_lens(prev_word, ids_and_posit_lens)
                ids_and_posit_lens = []
            else: print >>sys.stderr, 'NOT success', prev_word, prev_w_id

    # -----------------------------------------------------------
    if   (len(splt) == 3) and (NON_WORD_CHAR in word):
        doc_id, doc_len = int(splt[1]), int(splt[2])
        # Собираем посчитанные длины документов
        Ls.append( (doc_id, doc_len) )
        del splt

    # -----------------------------------------------------------
    elif (len(splt) == 4) and (NON_WORD_CHAR not in word):

        id, posit, hash = int(splt[1]), int(splt[2]), int(splt[3])
        if  prev_w_id and id != prev_w_id and (word == prev_word):
            
            len_ph = len(posits_and_hashes)
            success = send_posits_and_hashes(prev_word, prev_w_id, posits_and_hashes)
            posits_and_hashes = []

            # -----------------------------------------------------------
            if  success:  
                # Для каждого слова собираем документы и число вхождений
                ids_and_posit_lens.append( (int(prev_w_id), len_ph) )
            else: print >>sys.stderr, 'NOT success', prev_word, prev_w_id

        # Собираем позиции и хэши
        posits_and_hashes.append( (int(posit), int(hash)) )
        prev_w_id = id

    # -----------------------------------------------------------
    else:  print >>sys.stderr, 'line:', line
    prev_word = word

# -----------------------------------------------------------
# Не забыть, отправить последнее
send_lens(Ls);  Ls = []

send_posits_and_hashes(prev_word, prev_w_id, posits_and_hashes)
posits_and_hashes  = []

send_doc_ids_and_lens(prev_word, ids_and_posit_lens)
ids_and_posit_lens = []
# -----------------------------------------------------------


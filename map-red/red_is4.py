#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64encode
from operator import itemgetter

import array
import codecs
import sys
import re

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# -----------------------------------------------------------
# Выбор архиватора
if   (len(sys.argv) > 1 and sys.argv[1] == '-f'):
    module = importer.load_module('fib_archive')
    archiver = module.FibonacciArchiver()

elif (len(sys.argv) > 1 and sys.argv[1] == '-s'):
    module = importer.load_module('s9_archive')
    archiver = module.Simple9Archiver()

else: raise Exception("Have NO archiver-argument")


def print_log(pref, word, postf):
    print >>sys.stderr, (unicode(pref) + ' ' + word + ' ' + \
                         unicode(postf)).encode('ascii', 'ignore')
# -----------------------------------------------------------
def append_and_correct(arr, sub, num, len, last_num, inv=False):
    if  inv:
        j = last_num 
        while num - j > 1:
            j += 1
            arr.append(j - last_num)
        last_num = j
        return last_num
    
    # Уточняем номера
    arr.append(num - last_num)
    sub.append(len)
    # return  (arr, sub)
    last_num = num
    return last_num


NON_WORD_CHAR = u'$'
def send_docs_lens (ids, lens):
    """ """
    if  len(ids) < 1:
        print_log("NO doc_ids and lens","","")
        return False

    # всё архивируем вместе
    to_code = ids
    to_code.extend(lens)
    to_code.insert(0, len(ids))
    del ids, lens
    coded = archiver.code(to_code)
    del to_code
    # сразу отправляем, забываем
    print u'%s\t%s' % ( NON_WORD_CHAR, b64encode(coded) )
    del coded
    # success
    return True

# -----------------------------------------------------------
def send_doc_ids_and_lens  (word, ids, len_posits, part):
    """ """
    if  len(ids) < 1:
        print_log('ids:', word, len(ids))
        return False

    # Архивируем их
    coded_ids  = archiver.code(ids)
    del ids
    coded_lens = archiver.code(len_posits)
    del len_posits

    # И отправляем
    print u'%s\t%06d\t%06d\t%s\t%s' % (word, 0, part, \
            b64encode(coded_ids), b64encode(coded_lens))
    del coded_ids, coded_lens
    # success
    return True

# -----------------------------------------------------------
def send_posits_and_hashes (word, id, posits, hashes):
    """ """
    if  len(posits) < 1:
        print_log('posits:', word, str(id) + str(len(posits)))
        return False

    # архивируем
    coded_pos = archiver.code(posits)
    del posits
    coded_hss = archiver.code(hashes)
    del hashes
    # и отправляем          
    print u'%s\t%06d\t%06d\t%s\t%s' % (word, (int(id) + 1), 0, \
            b64encode(coded_pos), b64encode(coded_hss))
    del coded_pos, coded_hss
    # success
    return True

# -----------------------------------------------------------
# State
prev_word = None
prev_w_id = None

last_all = 0
all_doc_ids  = array.array('i',[])
all_doc_lens = array.array('i',[])

last_id = 0
word_doc_ids  = array.array('i',[])
word_doc_lens = array.array('i',[])
word_doc_ids_part = 0

last_posit = 0
doc_posits = array.array('i',[])
doc_hashes = array.array('i',[])

use_inverted = False
len_ids = 0

# Используем unicode в стандартных потоках io
sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
# sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

too_mush = 95000
re_spaces = re.compile(ur'[\t]')
# -----------------------------------------------------------
for line in sys.stdin:

    splt = re_spaces.split(line)
    word = splt[0]

    # -----------------------------------------------------------
    if   prev_word and (word != prev_word):

        if  NON_WORD_CHAR in prev_word:
            send_docs_lens(all_doc_ids, all_doc_lens);

            last_all = 0
            all_doc_ids  = array.array('i',[])
            all_doc_lens = array.array('i',[])

        else:
            len_ph = len(doc_posits)

            success = send_posits_and_hashes(prev_word, prev_w_id, \
                                             doc_posits, doc_hashes)

            last_posit = 0
            doc_posits = array.array('i',[])
            doc_hashes = array.array('i',[])

            # -----------------------------------------------------------
            if  success:
                # Для каждого слова собираем документы и число вхождений
                last_id = append_and_correct(word_doc_ids, word_doc_lens, \
                                             prev_w_id, len_ph, last_id)
                
                send_doc_ids_and_lens(prev_word, word_doc_ids, \
                                      word_doc_lens, \
                                      word_doc_ids_part)
                word_doc_ids_part = 0
                
                last_id = 0
                word_doc_ids  = array.array('i',[])
                word_doc_lens = array.array('i',[])

            else: print_log('NOT success:', prev_word, prev_w_id)

    # -----------------------------------------------------------
    if   (len(splt) == 4) and (NON_WORD_CHAR in word):
        doc_id, doc_len = int(splt[1]), int(splt[3])
        del splt
        # Собираем посчитанные длины документов
        last_all = append_and_correct(all_doc_ids, all_doc_lens, \
                                      doc_id, doc_len, last_all)

    # -----------------------------------------------------------
    elif (len(splt) == 4) and (NON_WORD_CHAR not in word):

        id, posit, hash = int(splt[1]), int(splt[2]), int(splt[3])
        del splt
        
        if  prev_w_id and id != prev_w_id and (word == prev_word):
            
            len_ph = len(doc_posits)
            success = send_posits_and_hashes(prev_word, prev_w_id, \
                                             doc_posits, doc_hashes)
            
            last_posit = 0
            doc_posits = array.array('i',[])
            doc_hashes = array.array('i',[])

            # -----------------------------------------------------------
            if  success:  
                # Для каждого слова собираем документы и число вхождений
                last_id = append_and_correct(word_doc_ids, word_doc_lens, \
                                             prev_w_id, len_ph, last_id)

                if  len(word_doc_ids) > too_mush:
                    # use_inverted = True
                    print_log('must use inversed:', word, prev_w_id)

                    send_doc_ids_and_lens(prev_word, word_doc_ids, \
                                          word_doc_lens, \
                                          word_doc_ids_part)
                    word_doc_ids_part += 1

                    last_id = 0
                    word_doc_ids  = array.array('i',[])
                    word_doc_lens = array.array('i',[])

            else: print_log('NOT success:', prev_word, prev_w_id)

        # Собираем позиции и хэши
        last_posit = append_and_correct( doc_posits, doc_hashes,
                                         posit, hash, last_posit )
        prev_w_id = id

    # -----------------------------------------------------------
    else:  print_log('line:', line, '')
    prev_word = word

# -----------------------------------------------------------
# Не забыть, отправить последнее
send_docs_lens(all_doc_ids, all_doc_lens);
del all_doc_ids, all_doc_lens

send_posits_and_hashes(prev_word, prev_w_id, doc_posits, doc_hashes)
del doc_posits, doc_hashes

send_doc_ids_and_lens(prev_word, word_doc_ids, word_doc_lens, word_doc_ids_part)
del word_doc_ids, word_doc_lens
# -----------------------------------------------------------


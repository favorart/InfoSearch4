#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
# import numpy as np

import zipimport
importer = zipimport.zipimporter('bs123.zip')


# if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
#     fib_archive = importer.load_module('fib_archive')
#     # all_docs= povarenok:199456, lenta:564548
#     max_number = int(sys.argv[2]) # max(199460, 564550)
#     archiver = fib_archive.FibonacciArchiver( max_number )
# 
# elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
#     s9_archive = importer.load_module('s9_archive')
#     archiver =  s9_archive.Simple9Archiver   ()
# 
# else: raise ValueError

class TextSearch(object):
    """ """
    def __init__(self, bs, syn_name='./data/RusSyn.txt'):
        """ """
        self.bs = bs

        self.syns = {}
        with codecs.open(syn_name, 'r', encoding='utf-8') as f_syn:
            for line in f_syn:
                splt = line.rstrip().split(u'|')
                if splt > 1:
                    word = splt[0]
                    norm = mylex.norm(word)
                    syns[norm] = splt.split(u',')
                    syns[norm].insert(word)
                    
    def search():
        """ """
        return 0

    """ 
        Passage
        Алгоритм:
    
        Пассаж - фрагмент документа, 
        размера, не превышающего заданный, в котором 
        встречаются все термы запроса, либо значительная 
        часть термов запроса, суммарный IDF которых 
        превышает заданное ограничение. 
        
        Скользящее окно 


        Оцениваем каждый пассаж 
        - tf-idf  
        - Полнота 
        - Порядок слов 
        - Правильность словоформ 
        - Кучнсть 
        - Близость к началу 
        - Особенность зоны 
        Ранг пассажа = линейная комбинация оценок 

        набор нескольких релевантных вхождений, которые расположены не слишком далеко друг от друга. Для поиска пассажей используется алгоритм скользящего окна. Скользящее окно — это массив, каждый элемент которого соответствует слову из запроса.  Двигаясь по релевантным вхождениям мы пытаемся связать их с ячейками скользящего окна. Каждый матчинг приводит к формированию пассажей (см рисунок).  Каждый сформированный пассаж численно оценивается по следующим показателям
        •	Полнота: %слов из запроса в пассажей
        •	Расстояние от начала документа.
        •	Кучность, как число слов не из пассажа между словами пассажа
        •	tf-idf ранк пассажа
        •	Порядок слов
        Каждый параметр должен отражать качество пассажа по принципу чем больше — тем лучше.

        Далее, выводится итоговый ранк пассажа, как линейная комбинация параметров пассажа  с коэффициентами.  В первом приближении коэффициенты можно установить в 1, далее их нужно будет настроить.

        В процессе поиска пассажей мы запоминаем ранк лучшего пассажа, он и будет является пассажным ранком документа.

        Итоговый ранг: вес tf-idf + вес парного tf-idf + вес пассажного алгоритма

        В пассажном алгоритме у вас есть 5 параметров, которые нужно подобрать методом дифференциальной эволюции 
    """
    def __init__(self):
        """ """
        # 1. Полнота
        # 2. Слово-форма
        # 3. Компактность
        # 4. Порядок слов
        # 5. Неповторяемость слов
        # 6. Длина предложения от оптимального
        # 7. Близость к началу
        pass

    def sentence_rank(self, sentence, query_words, in_sentence, len_text):
        """ norm: string, word: string, byte_pos: int

            sentence     - sentence[0] - begin:     int
                           sentence[1] - end:       int
                           sentence[2] - sentence:  string
            query_words  - normal words in query:   [(norm, word, no)] 
            in_sentence  - words in sentence (positions with repeats):
                           { (norm1, word1):[pos],
                             (norm2, word2):[pos0, pos1, ...],
                             ... }

            Returns the vector of sentence characteristics
                -->  maximaze to get the best
        """
        sent_cls = float(sentence[0]) / len_text # begin
        sent_len = fabs(self.snippet_len - (sentence[1] - sentence[0])) / self.snippet_len

        # print sentence[2][:20].encode('cp866', 'ignore')
        # print 'sent_len=', fabs(self.snippet_len - (sentence[1] - sentence[0])), self.snippet_len
        # print 'fullness=', len(in_sentence), len(query_words)
        
        fullness = 1. - float(len(in_sentence)) / len(query_words)
        # на самом деле в запросе могут быть тоже разные слово формы
        # n_norms_in_query = float(len(set([ norm for norm, word, pos  in query_words ])))
        # n_norms_in_sents = float(len(set([ norm for norm, word, poss in in_sentence ])))
        # fullness -= n_norms_in_sents / n_norms_in_query

        mw_forms = 0.
        # word form is equal?  --> min
        for norm, word, poss in in_sentence:
            for q_norm, q_word, w_pos in query_words:
                if q_norm == norm:
                    diffs = [ dif for dif in difflib.ndiff(q_word, word) if dif and (dif[0] == '+' or dif[0] == '-') ]
                    # print '\n'.join(diffs).encode('cp866', 'ignore')
                    # print 'diffs=', len(diffs), max(len(q_word), len(word))
                    mw_forms += len(diffs) / max(len(q_word), len(word))

        compacts = 0.
        poss = sorted([ pos for norm, word, poss in in_sentence for pos in poss ])
        for i in xrange(len(poss) - 1, 0, -1):
            compacts += poss[i] - poss[i-1]
        # print 'compacts=', compacts, (poss[-1] - poss[0] + 1)
        compacts /= (poss[-1] - poss[0] + 1)

        n_repeat = 1.
        for norm, word, poss in in_sentence:
            n_repeat *= len(poss)
        # print 'n_repeat=', n_repeat, len(poss)
        n_repeat /= len(poss)
        
        mw_order = 0.
        # itertools <-- TODO: !!!

        # --> min
        vector = ( 1. - fullness, 1. - mw_forms, 1. - compacts,
                   1. - n_repeat, 1. - mw_order,
                   1. - sent_len, 1. - sent_cls )
        # --> max
        return vector

    def rank(self):
        """ """



#!/usr/bin python
# -*- coding: utf-8 -*-

import re
import sys
sys.path.insert(0, 'map-red')

import copy
import codecs
import itertools
from operator import itemgetter

from BlackSearch import BlackSearch, BooleanSearch

# import numpy as np
import pickle



class TextSearch(object):
    """ Пассажный алгоритм:
    
        Пассаж - фрагмент документа, размера, не превышающего заданный, в котором 
        встречаются все термы запроса, либо значительная часть термов запроса, 
        суммарный IDF которых превышает заданное ограничение. Набор нескольких 
        релевантных вхождений, которые расположены не слишком далеко друг от друга.

        Скользящее окно — это массив, каждый элемент которого соответствует слову из запроса.
        Двигаясь по релевантным вхождениям мы пытаемся связать их с ячейками скользящего окна.
        Каждый матчинг приводит к формированию пассажей.  
        
        Пассажный ранг документа - ранг лучшего пассажа в документе.
        Итоговый ранг: вес(tf-idf) + вес(пассажного алгоритма)   (+ вес(парного tf-idf))
    """
    def __init__(self, br,
                 stops_filename='./data/StopWords.txt',
                 use_synonyms=False,
                 synonyms_filename='./data/RusSyn.txt'):
        """ Constructor """
        self.min_len_meanful_word = 3
        with codecs.open(stops_filename, 'r', encoding='utf-8') as f_stops:
            self.stops = set(map(lambda line: line.strip().rstrip('\n'), f_stops.readlines() ))

        self.use_synonyms = use_synonyms
        if  use_synonyms:
            self.syns = {}
            with codecs.open(synonyms_filename, 'r', encoding='utf-8') as f_syn:
                for line in f_syn:
                    splt = line.rstrip().split(u'|')
                    if splt > 1:
                        norm = br.lex.norm(splt[0])
                        self.syns[norm] = list(set([norm] + splt[1].split(u',')))
        self.br = br
        self.params = [1.] * 7
                      # [6.029999999999999, 2.0699999999999985, 9.0, 1.08, \
                      #  2.0700000000000003, 3.059999999999999, 3.059999999999999]

    def filter_by_stops(self, query_norms):
        """ Return two (meanful and another) lists of words """
        means, stops = [], []
        for norm in query_norms:
            if (len(norm) >= self.min_len_meanful_word) \
                and (norm not in self.stops):
                means.append(norm)
            else:
                stops.append(norm)
        return  (means, stops)

    def formulate_request(self, query):
        """ Bool Search string
        
            Returns uniq_query_norms, query_norms_hashes, request
        """
        # Ordered query
        query__n_h = [ self.br.lex.normalize(word) for word in query.lower().split() ]
        # unique non-ordered normal forms of word in query
        query_norms = list(set(map(itemgetter(0),query__n_h)))

        query_means, query_stops = self.filter_by_stops(query_norms)
        
        query_syns = []
        if  self.use_synonyms:
            query_syns
            for i in xrange(len(query_means)):
                norm = query_means[i]
                try:
                    # Append synonims to request
                    query_syns += self.syns[norm]
                except: continue

        request = query_means + query_stops + query_syns
        return (query__n_h, query_means, request)
                            
    def search(self, query, max_n_docs=1000, use_synonyms=False, mark_id=None, f_params=None):
        """ Returns the  doc_scores: (doc_id, total_rank) """
        query__n_h, query_means, request = self.formulate_request(query)

        inv_q = self.br.lex.incorrect_keyboard_layout(query)
        if  inv_q:
            inv_q__n_h, inv_q_means, inv_q_req = self.formulate_request(inv_q)
            # Append inversed to request line
            query__n_h += inv_q__n_h
            query_means += inv_q_means
            request += inv_q_req

        trs_q = self.br.lex.transliterate(query)
        if  trs_q:
            trs_q__n_h, trs_q_means, trs_q_req = self.formulate_request(trs_q)
            # Append transliterated to request line
            query__n_h += trs_q__n_h
            query_means += trs_q_means
            request += trs_q_req

        query_index, indexed_doc_ids = self.br.search(request,
                                                      up=["ids", "lens", "posits", "hashes"],
                                                      verbose=True)

        # query_index  is  { norm: [ "ids", "lens", "posits", "hashes" ], ... }
        query_norms = query_index.keys()
        query__n_h = [ (norm, hash)  for norm, hash in query__n_h  if norm in query_norms ]

        # If there are STOPs - OK, if not, it is also OK!
        intersect_doc_ids = set(indexed_doc_ids)
        for word, index in query_index.items():
            if word in query_means:
                intersect_doc_ids &= set(index['ids'])
        # ?? synonyms
        intersect_doc_ids = list(intersect_doc_ids)

        tfs, idfs  = self.br.tf_idf(query_index, intersect_doc_ids)
        doc_scores = self.br.ranking(query_norms, query_index, intersect_doc_ids, tfs, idfs)

        if mark_id:
            res = [ (i,score[1]) for i,score in enumerate(doc_scores) if score[0] == mark_id ]
            print >>f_params, "mark_id:", res if res else "none"
            print             "mark_id:", res if res else "none"

        # choose documents to ranking by passage algorithm
        doc_bm25_scores = doc_scores[:max_n_docs]

        doc_pssg_scores = []
        for doc_id, score in doc_bm25_scores:
            best_passage_rank = self.ranking(query_norms, query__n_h,
                                             query_index, doc_id,
                                             tfs, idfs)
            doc_pssg_scores.append( (doc_id, best_passage_rank) )

        # sort by ids
        doc_pssg_scores.sort(key=itemgetter(0))
        doc_bm25_scores.sort(key=itemgetter(0))

        if mark_id:
            res = [ (i,score[1]) for i,score in enumerate(doc_pssg_scores) if score[0] == mark_id ]
            print             "mark_id pssg:", res if res else "none"
            print >>f_params, "mark_id pssg:", res if res else "none"
            print >>f_params, '\n'
            print             '\n'

        # total rank
        doc_scores = map(lambda x, y: (x[0], sum(x[1]) + y[1]), doc_pssg_scores, doc_bm25_scores)
        # sort by rank
        doc_scores.sort(key=itemgetter(1), reverse=True)
        print doc_scores[:5]

        doc_ids = [ score[0] for score in doc_scores ]
        return doc_ids

    def sliding_window(self, query__n_h, doc_text):
        """ Скользяцее окно """
        passages = []
        N = len(query__n_h)

        passage = []
        norms_psg = set()
        for norm, posit, hash in doc_text:

            if  norm in norms_psg:
                for i in xrange(len(passage)):
                    if passage[i][0] == norm:
                        del passage[i]
                        break
            else:
                norms_psg.add(norm)

            if len(passage) == N:
                in_psg.remove(passage[0][0])
                del passage[0]
            
            passage.append( (norm, posit, hash) )
            passages.append( copy.copy(passage) )
        return passages

    def passage_rank(self, passage, passage_norms, query_norms, query__n_h, doc_id):
        """ Каждый пассаж численно оценивается по следующим показателям:
            •	Полнота:      %слов из запроса в пассажей, все ли слова представлены
            •	Расстояние    от начала документа
            •	Кучность:     как число слов не из пассажа между словами пассажа
            •	Слово-форма:  различие слово-форм в пассаже
            •	Порядок слов: транспозиции
            •	tf-idf        ранг пассажа
            Returns the vector of passage characteristics
            -->  maximaze to get the best
        """
        # passage item: norm, posit, hash
        fullness = float(len(passage_norms)) / len(query_norms)

        psg_range = (passage[-1][1] - passage[0][1]) + 1.
        psg_range = float(len(passage) if psg_range < len(passage) else psg_range)
        compactness = 1. - (psg_range - len(passage)) / psg_range

        len_text = self.br.doc_lens[doc_id]
        close2start = 1. - float(passage[0][1]) / len_text

        words_form = 0.
        forms = [ (n,h) for n,p,h in passage ]
        for norm,hash in query__n_h:
            if (norm,hash) in forms:
                forms.remove( (norm,hash) )
                words_form += 1.
        words_form /= len(query__n_h)

        all_trs, eq_trs = 0., 0.
        q_transpositions = itertools.combinations(range(len(query__n_h)), 2)
        p_transpositions = itertools.combinations(range(len(passage)), 2)
        for i,j in q_transpositions:
            for p,q in p_transpositions:
                if  query__n_h[i][0] == passage[p][0] and \
                    query__n_h[j][0] == passage[q][0]:
                    eq_trs += 1.
                all_trs += 1.
        words_order = eq_trs / all_trs if all_trs else 0.
        # --> max
        return (fullness, compactness, close2start, words_form, words_order)

    def ranking(self, query_norms, query__n_h, query_index, doc_id, tfs, idfs):
        """ """
        doc_text = []
        for word, index in query_index.items():
            try:
                doc_index = index["ids"].index(doc_id)
            except: continue
            posits, hashes = self.br.bs.decode_posits_and_hashes_for_doc(index, doc_index)
            doc_text += zip([word] * min(len(posits), len(hashes)), posits, hashes)

        doc_text.sort(key=itemgetter(1))

        doc_passages = self.sliding_window(query__n_h, doc_text)

        doc_passages_ranges = []
        for i, passage in enumerate(doc_passages):
            passage_norms = list(set([ n for n,p,h in passage ]))

            doc_score = self.br.ranking(passage_norms, query_index, [doc_id], tfs, idfs)
            doc, tf_idf = doc_score[0]

            vector = self.passage_rank(passage, passage_norms, query_norms, query__n_h, doc_id)
            # НОРМИРОВАННЫЕ ВЕЛИЧИНЫ:
            #   1. Полнота
            #   2. Компактность
            #   3. Близость к началу
            #   4. Слово-форма
            #   5. Порядок слов
            #   6. tf-idf пассажа
            # Итоговый ранк пассажа, как линейная комбинация
            # параметров пассажа с коэффициентами = 1.
            # --->> MAXIMIZE
            doc_passages_ranges.append( list(vector) + [tf_idf] )
            
        doc_passages_ranges.sort(key=lambda x: sum(x), reverse=True)
        return  doc_passages_ranges[0]

    def brute_coefs(self, marks):
        """ Алгоритм  дифференциaльной эволюции (differential evolution) 
       
            На каждой итерации генерируется множество векторов, называемых поколением, 
            случайным образом комбинируя векторы из предыдущего поколения.
            
            Для каждого вектора x_i из старого поколения выбираются три различных случайных вектора
            v_1, v_2, v_3 среди векторов старого поколения, за исключением самого вектора x_i, и
            генерируется так называемый мутантный вектор (mutant vector) по формуле:

            v = v_1 + F \cdot (v_2 - v_3),

            где F — один из параметров метода, некоторая положительная действительная константа в интервале [0, 2].

            Над мутантным вектором v выполняется операция «скрещивания» (crossover), состоящая в том, что некоторые
            его координаты замещаются соответствующими координатами из исходного вектора x_i (каждая координата
            замещается с некоторой вероятностью, которая также является еще одним из параметров этого метода).
            Полученный после скрещивания вектор называется пробным вектором (trial vector). 
            Если он оказывается лучше вектора x_i (то есть значение целевой функции стало меньше),
            то в новом поколении вектор x_i заменяется на пробный вектор, а в противном случае — остаётся x_i.
        """

        # fit 
        self.params


        return
    
    def pair_tf_idf(self):
        """ Вхождение терма в документ учитывается только в 
            том случае, если оно находится в документе на 
            расстоянии, не превышающим заданное от хотя бы 
            одного из стоящих рядом с ним термов запроса.
        """
        # TODO
        return



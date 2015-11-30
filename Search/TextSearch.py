#!/usr/bin python
# -*- coding: utf-8 -*-

import re
import sys
import copy
import codecs
import itertools
import numpy as np
from operator import itemgetter

import zipimport
importer = zipimport.zipimporter('bs123.zip')

from BlackSearch import BlackSearch, BooleanSearch


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
                 stp_name='./data/StopWords.txt',
                 syn_name='./data/RusSyn.txt'):
        """ Constructor """
        self.min_len_meanful_word = 3
        with codecs.open(stp_name, 'r', encoding='utf-8') as f_stops:
            self.stops = set(map(lambda line: line.strip().rstrip('\n'), f_stops.readlines() ))

        self.syns = {}
        with codecs.open(syn_name, 'r', encoding='utf-8') as f_syn:
            for line in f_syn:
                splt = line.rstrip().split(u'|')
                if splt > 1:
                    word = splt[0]
                    norm = mylex.norm(word)
                    syns[norm] = splt.split(u',')
                    syns[norm].insert(word)
        self.br = br

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

    def formulate_request(self, query, use_synonyms):
        """ Bool Search string """
        query__n_h = [ self.lex.normalize(word) for word in query.lower().split() ]
        query_norms = map(itemgetter(0),query__n_h)

        query_means, query_stops = self.filter_by_stops(query_norms)

        if  use_synonyms:
            for i in xrange(len(query_means)):
                norm = query_means[i]
                try:
                    syns = self.syns[norm]
                except: continue
                syns = list(set(syns + [norm]))
                # Append synonims to request
                query_means[i] = ' OR '.join(syns)

        joined_means = u' AND '.join(query_means)
        joined_norms = u' AND '.join(query_norms)

        joined_query = u' OR '.join([ joined_means, joined_norms ])
        return (query_norms, query__n_h, joined_query)
                            
    def search(self, query, max_n_docs=1000, use_synonyms=False):
        """ Returns the  doc_scores: (doc_id, total_rank) """
        query_norms, query__n_h, request = self.formulate_request(query)

        inv_q = self.lex.incorrect_keyboard_layout(query)
        if inv_q:
            inv_request = self.formulate_request(inv_q)
            request = inv_request + ' OR ' + request

        request_words = request.split(' ')
        query_index, indexed_doc_ids = self.br.search_docs(request_words)
        # query_index = { norm: [ "ids", "lens", "posits", "hashes" ], ... }

        tfs, idfs  = self.br.tf_idf(query_index)
        doc_scores = self.br.ranking(query_index, indexed_doc_ids, tfs, idfs)

        # choose documents to ranking by passage algorithm
        doc_bm25_scores = doc_scores[:max_n_docs]

        doc_pssg_scores = []
        for doc_id in [ id for id, score in doc_bm25_scores ]:
            best_passage_rank = self.ranking(doc_id)
            doc_pssg_scores.append( (doc_id, best_passage_rank) )

        doc_pssg_scores.sort(key=itemgetter(0))
        doc_bm25_scores.sort(key=itemgetter(0))

        doc_scores = (doc_pssg_scores + doc_bm25_scores) # total rank
        doc_scores.sort(key=itemgetter(1), reverse=True)
        return  doc_scores

    def sliding_window(self, query_norms, doc_text):
        """ """
        N = len(query_words)

        passages = []
        for item in doc_text:
            passage = []

            # item: norm, posit, hash
            if len(passage) == N:
                for i in len(passage):
                    if passage[i][0] == item[0]:
                        del passage[i]
                        break
                else: del passage[0]

            passage.append(item)
            passages.append( copy.copy(passage) )

        return passages

    def passage_rank(self, passage, query__n_h, uniq_query_norms, doc_id):
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
        query_norms = uniq_query_norms
        # passage item: norm, posit, hash
        psg_norms, psg_posits, psg_hashes = zip(*passage)

        fullness = sum([ float(norm in psg_norms) for norm in query_norms ]) / len(query_norms)

        psg_range = passage[-1][1] - passage[0][1]
        compactness = float(psg_range - len(passage)) / psg_range

        len_text = self.br.doc_lens[doc_id]
        close2start = float(passage[0][1]) / len_text

        # !!!!!!!!!!!
        # words_form = 0.
        # for p_norm, p_group in itertools.groupby(passage, key=itemgetter(0)):
        #     # for norm, group in itertools.groupby(query__n_h, key=itemgetter(0)):
        #     hashes = passage
        #     for norm, hash in query__n_h:
        #         if norm == p_norm and hash in passage_hashes:
        #             words_form += 1

        all_trs, eq_trs = 0, 0
        transpositions = itertools.combinations(len(query__n_h), 2)
        for i,j in transpositions:
            if query__n_h[i][0] == passage[i] and \
               query__n_h[j][0] == passage[j]:
                eq_trs += 1
            all_trs += 1
        words_order = eq_trs / all_trs

        # --> max
        return (fullness, compactness, close2start, words_form, words_order)

    def ranking(self, query__n_h, query_norms, query_index, doc_id, tfs, idfs):
        """ """
        doc_text = []
        for word, index in query_index.items():
            try:
                doc_index = index["ids"].index(doc_id)
            except: continue
            posits, hashes = self.br.bs.decode_posits_and_hashes_for_doc(query_index, doc_index)
            doc_text += zip([word] * len(posits), posits, hashes)

        doc_text.sort(key=itemgetter(1))

        doc_passages = self.sliding_window(query_norms, doc_text)

        # !!!
        query_norms = list(set(query_norms))

        doc_passages_ranges = []
        for i, passage in enumerate(doc_passages):

            tf_idf = self.br.rank_docs(answer, [doc_id], tfs, idfs)
            vector = self.passage_rank(passage, query__n_h, query_norms, doc_id)
            vector.append(tf_idf)
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
            doc_passages_ranges.append(sum(vector)) # , i)
            
        doc_passages_ranges.sort(reverse=True)
        return  doc_passages_ranges[0]
    
    def pair_tf_idf():
        """ Вхождение терма в документ учитывается только в 
            том случае, если оно находится в документе на 
            расстоянии, не превышающим заданное от хотя бы 
            одного из стоящих рядом с ним термов запроса.
        """
        # TODO
        return



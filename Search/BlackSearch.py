#!/usr/bin python
# -*- coding: utf-8 -*-

from operator import itemgetter
from math import *
import codecs
import sys
sys.path.insert(0, 'map-red')

import re

import utils
from BoolSearch import BooleanSearch


class BlackSearch(object):
    """ Алгоритм BM25:        
        + Для каждого документа, который находит булев поиск,
          вычисляем tf-idf-ранг.
        + Отбираем 100-1000 документов с максимальным рангом.
    """
    def __init__(self, bs, lex, dlen_name='/data/dlens.txt'):
        """ Constructor """
        self.lex = lex
        self.bs = bs
        
        with open(dlen_name, 'r') as f_dlens:
            splt = f_dlens.readline().strip().rstrip('\n').split('\t')
            if len(splt) == 2:
                # N - кол-во документов в корпусе
                self.N = int(splt[0])
                # длины документов в корпусе
                mapped = map( lambda x: x.split(','), splt[1].split(' ') )
                self.doc_lens = dict(map(lambda x: (int(x[0]), int(x[1])), mapped))
        # Коэффициенты алгоритма
        self.k = 2.
        self.b = 0.75
        # средняя длина документа в корпусе
        self.A = float(sum( self.doc_lens.values() )) / self.N

    def tf_idf(self, query_words_index, intersect_doc_ids=None):
        """ tf-idf
            query_words_index:
            { 'word': { 'ids'  : [doc_id,   ... ],
                        'lens' : [n_coords, ... ],
                        ... }, ... }

            Returns tfs, idfs
        """
        tfs, idfs = {}, {}
        dic = query_words_index
        for word, index in dic.items():
            tfs[word] = {}

            doc_ids = intersect_doc_ids if intersect_doc_ids else index['ids']
            for doc_id, n_coords in zip(doc_ids, index['lens']):
                tfs[word][doc_id] = 1. + log10(float(n_coords))

            n_docs = float(len(index['ids']))
            idfs[word] = log10(float(self.N) / n_docs)
        return (tfs, idfs)

    def search(self, query_norms, up=["ids", "lens"], verbose=False):
        """ Request to DB
            query_norms: without repeats
            
            Returns query_words_index,
                    doc_ids - ids of the all found documents
        """
        doc_ids = set()
        query_words_index = self.bs.extract(query_norms, up=up, verbose=verbose)
        for word, dic in query_words_index.items():
            if dic['ids']: doc_ids |= set(dic['ids'])

        doc_ids = list(doc_ids)
        doc_ids.sort()
        return  query_words_index, doc_ids

    def ranking(self, query_norms, query_words_index, doc_ids, tfs, idfs):
        """ answer  = { "norm": [ "ids", "lens", "posits", "hashes" ], ... }
            doc_ids = [ ... ] 

            tfs[word][doc_id] = 1. + log10(n_coords)
            idfs[word] = log10(N / word_n_docs)
            score[doc_id] = sum_word (tf * idf) / ( k * (1. - b + b * L / A) + tf )

            Returns the document scores: (doc_id, score)
        """
        A = self.A
        k = self.k
        b = self.b

        doc_scores = []
        for doc_id in doc_ids:
            L = self.doc_lens[doc_id]

            score = 0.
            for word in query_norms:
                try:
                    tf  = tfs  [word][doc_id]
                    idf = idfs [word]
                except: continue

                score += (tf * idf) / ( k * (1. - b + b * L / A) + tf )
            doc_scores.append( (doc_id, score) )

        # idf > 0, выкидываем стоп слова
        if len(doc_ids) > 1:
            doc_scores.sort(key=itemgetter(1), reverse=True)
        return doc_scores



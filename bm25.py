import sys
from math import *


class bm25(object):
    """ Алгоритм:        
        + для каждого документа, который находит булев поиск,
          вычисляем bm25-ранг.
        + Очередь с приоритетами - отбираем 100-1000 документов
          с максимальным рангом.
    """

    def __init__(self):
        # self.
        return

    def ranking(self, dic, N):
        """ dic = {norm1: [ word1,
                            doc_id1, coords, coord1, coord2, ...,
                            doc_id2, coords, ... ] ,
                   norm2: [ word2, 
                            doc_id1, coords, ... ] , ... }
        """
        
        word_docs = []
        """ tf-idf """
        tfs = {}
        idfs = {}
        for i, word, index in enumerate(dic.items()):
            
            j = 1
            n_docs = 0
            while j < len(index):
                n_coords = index[j + 1]

                doc_id = index[j]
                coords = index[j : j + n_coords]                
                n_docs += 1

                j += shift
                tfs[(word, index[j])] = (1. + log10(len(coords)), coords)
            idfs[word] = (log10(N / n_docs), n_docs)

        # score(q,d) = sum_(t in q and d) (tf * idf)

        #  (tf * idf) / ( k * (1 - b + b * L/A) + tf )

        # idf > 0, выкидываем стоп слова

        #   N - кол-во документов в корпусе
        #   L - длина документа
        #   A - средняя длина документа в корпусе
        #   k = 2, b = 0.75 - коэффициенты





from math import *
import sys
import re


import zipimport
importer = zipimport.zipimporter('bs123.zip')
    
if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    fib_archive = importer.load_module('fib_archive')
    # all_docs= povarenok:199456, lenta:564548
    max_number = int(sys.argv[2]) # max(199460, 564550)
    archiver = fib_archive.FibonacciArchiver( max_number )

elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    s9_archive = importer.load_module('s9_archive')
    archiver =  s9_archive.Simple9Archiver   ()

else: raise ValueError


from utils import MyLex
from BoolSearch import BooleanSearch

class BlackRank(object):
    """ Алгоритм BM25:        
        + для каждого документа, который находит булев поиск,
          вычисляем bm25-ранг.
        + Очередь с приоритетами - отбираем 100-1000 документов
          с максимальным рангом.
    """
    def __init__(self, bs, lex, dlen_name='/data/dlens.txt', stp_name='./data/StopWords.txt'):
        """ """
        self.lex = lex
        self.bs = bs

        self.min_len_meaning_word = 3
        with codecs.open(stp_name, 'r', encoding='utf-8') as f_stops:
            self.stops = set(filter( lambda line: line.strip().rstrip('\n'), f_stops.readlines() ))

        with open(dlen_name, 'r') as f_dlens:
            splt = f_dlens.readline().strip().rstrip('\n').split('\t')
            if len(splt) == 2:
                # N - кол-во документов в корпусе
                self.N = int(splt[0])
                # длины документов в корпусе
                self.doc_lens = filter(lambda i: int(i), splt[1].split(' '))
        # Коэффициенты алгоритма
        self.k = 2.
        self.b = 0.75
        # средняя длина документа в корпусе
        self.A = sum(self.doc_lens) / self.N

    def filter_by_stops(self, query_words):
        """ """
        filtered, stops = [], []
        for word in query_words:
            if (len(word) >= self.min_len_meaning_word) \
                and (word not in self.stops):
                filtered.append(word)
            else:  stops.append(word)
        return filtered, stops

    def tf_idf(self, dic):
        """ tf-idf
        
            dic: { word: [(doc_id, n_coords), ... ] ... }
        """
        tfs, idfs = {}, {}
        for i, word, index in enumerate(dic.items()):
            
            tfs[word] = {}
            n_docs = len(index)
            
            for doc_id, n_coords in index:
                tfs[word][doc_id] = 1. + log10(n_coords)

            idfs[word] = (log10(self.N / n_docs), n_docs)
            return (tfs, idfs)

    def search(self, query):
        """ dic = { norm: [ (doc_id, n_coords), ... ], ... } """
        query_norms = list(set(filter( lex.norm(w) for w in query.split() )))
        query_filtered, query_stops = self.filter_by_stops(query_norms)

        dic, answers = {}, []
        for word in query_norms:
            # if query_words != query_filtered: pass else:
            answer = bs.search(query_filtered, query_stops)
            dic[word] = answer
            answers += answer

        answers = list(set(answers))
        tfs, idfs = self.tf_idf()

        # score(q,d) = sum_(t in q and d) (tf * idf)

        score = {}
        for doc_id in answers:
            tf = tfs[word][doc_id]
            idf = idfs[word]

            A = self.A
            L = self.doc_lens[doc_id]

            score[doc_id] = 0
            for word in query_words:
                score[doc_id] += tf / ( k * (1. - b + b * L / A) + tf )
            score[doc_id] *= idf

        # idf > 0, выкидываем стоп слова
        return score


def black_rank():
    """ """
    blk_rank = sys.argv[3] if len(sys.argv) > 3 else './data/povarenok1000_black_rank.txt'
    bin_name = sys.argv[4] if len(sys.argv) > 4 else './data/povarenok1000_backward.bin'
    ndx_name = sys.argv[5] if len(sys.argv) > 5 else './data/povarenok1000_index.txt'
    ndx_lens = sys.argv[6] if len(sys.argv) > 6 else './data/povarenok1000_dlens.txt'
    mrk_name = sys.argv[7] if len(sys.argv) > 7 else 'C:\\data\\povarenok.ru\\all\\povarenok1000.tsv'
    url_name = sys.argv[8] if len(sys.argv) > 8 else 'C:\\data\\povarenok.ru\\1_1000\\urls.txt'

    urls = []
    with open(url_name, 'r') as f_urls:
        for line in f_urls.readlines():
            id, url = line.strip().split()
            url = re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', url)
            urls.append(url)

    br = BlackRank(bs=BooleanSearch(ndx_name, bin_name), lex=MyLex())

    found = 0
    with codecs.open(mrk_name, 'r', encoding='utf-8') as f_marks:
        for i,line in enumerate(f_marks.readlines()[2:]):
            splt = line.split('\t')
            if len(splt) == 2:
                query, mark_url = splt
                mark_url = re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', mark_url)

                answer = br.search(query)
                
                m = re.search(mark_url, ' '.join([ urls[i] for i in answer ]))
                if m is not None:
                    print (mark_url + ' ' + url)
                    found += 1
                    break
                # else: print '\t' + query.encode('cp866', 'ignore')
    print found


if __name__ == '__main__':
    black_rank()


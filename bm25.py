from math import *
from operator import itemgetter
import codecs
import sys
import re


import zipimport
importer = zipimport.zipimporter('bs123.zip')


import utils
# from utils import MyLex
from BoolSearch import BooleanSearch


class BlackRank(object):
    """ Алгоритм BM25:        
        + для каждого документа, который находит булев поиск,
          вычисляем bm25-ранг.
        + Очередь с приоритетами - отбираем 100-1000 документов
          с максимальным рангом.
    """
    def __init__(self, bs, lex, dlen_name='/data/dlens.txt', stp_name='./data/StopWords.txt'):
        """ Constructor """
        self.lex = lex
        self.bs = bs

        self.min_len_meaning_word = 3
        with codecs.open(stp_name, 'r', encoding='utf-8') as f_stops:
            self.stops = set(map(lambda line: line.strip().rstrip('\n'), f_stops.readlines() ))

        with open(dlen_name, 'r') as f_dlens:
            splt = f_dlens.readline().strip().rstrip('\n').split('\t')
            if len(splt) == 2:
                # N - кол-во документов в корпусе
                self.N = int(splt[0])
                # длины документов в корпусе
                self.doc_lens = map(lambda dlen: int(dlen), splt[1].split(' '))
        # Коэффициенты алгоритма
        self.k = 2.
        self.b = 0.75
        # средняя длина документа в корпусе
        self.A = float(sum(self.doc_lens)) / self.N

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
            dic: { 'word': { 'ids'  : [doc_id,   ... ],
                             'lens' : [n_coords, ... ],
                             ... }, ... }
        """
        tfs, idfs = {}, {}
        for word, index in dic.items():

            tfs[word] = {}
            for doc_id, n_coords in zip(index['ids'], index['lens']):
                tfs[word][doc_id] = 1. + log10(float(n_coords))

            n_docs = float(len(index['ids']))
            idfs[word] = log10(float(self.N) / n_docs)
        return (tfs, idfs)

    def search(self, query):
        """ dic = { norm: [ (doc_id, n_coords), ... ], ... } """
        doc_ids = set()
        query_norms = list(set([ self.lex.norm( w.lower() ) for w in query.split() ]))

        #     # if query_words != query_filtered: pass else:
        #     # answer = self.bs.search(query_norm, query_stops)

        # query_fltrs, query_stops = self.filter_by_stops(query_norms)
        # answer_fltrs = self.bs.extract(query_fltrs, up=['ids', 'lens'])
        # answer_stops = self.bs.extract(query_stops, up=['ids', 'lens'])
        # for word, dic in answer_fltrs: doc_ids += dic['ids']
        # for word, dic in answer_stops: doc_ids += dic['ids']

        answer = self.bs.extract(query_norms, up=['ids', 'lens'])
        for word, dic in answer.items():
            if dic['ids']:
                doc_ids |= set(dic['ids'])

        if not doc_ids:
            return None
        # OR
        tfs, idfs = self.tf_idf(answer)

        A = self.A
        k = self.k
        b = self.b
        doc_scores = []
        for doc_id in doc_ids:
            L = self.doc_lens[doc_id]

            score = 0
            for word in query_norms:
                try:
                    tf = tfs[word][doc_id]
                except: continue
                idf = idfs[word]

                score += (tf * idf) / ( k * (1. - b + b * L / A) + tf )
            doc_scores.append( (doc_id, score) )

        # idf > 0, выкидываем стоп слова
        doc_scores.sort(key=itemgetter(1), reverse=True)
        return doc_scores


def black_rank():
    """ """
    args = utils.parse_args()

    if  args.fib:
        fib_archive = importer.load_module('fib_archive')
        archiver = fib_archive.FibonacciArchiver(args.fib)

    elif args.s9:
        s9_archive = importer.load_module('s9_archive')
        archiver =  s9_archive.Simple9Archiver()

    with open(args.url_name, 'r') as f_urls:
        urls = map(lambda line: re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', \
                                line.strip().split()[1]), f_urls)
                   
    br = BlackRank( bs=BooleanSearch(args.ndx_name, args.bin_name, archiver), \
                    lex=utils.MyLex(), dlen_name=args.len_name)

    found = []
    with codecs.open(args.mrk_name, 'r', encoding='utf-8') as f_marks:
        for i,line in enumerate(f_marks.readlines()[10:]):
            splt = line.split('\t')
            if len(splt) == 2:
                query, mark_url = splt
                mark_url = re.sub(r'(?:^https?://(www\.)?)|(?:/?\r?\n?$)', '', mark_url)

                answer = br.search(query)
                if answer:
                    # m = re.search(mark_url, ' '.join([ urls[i] for i in answer ]))
                    # if m is not None:
                    found_urls = [ urls[i[0]] for i in answer ]
                    if  mark_url in found_urls:
                        index = found_urls.index(mark_url)
                        print (mark_url + ' ' + url)
                        found.append(index)
                        break
                # else: print '\t' + query.encode('cp866', 'ignore')
    print found


if __name__ == '__main__':
    black_rank()


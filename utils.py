import pymorphy2
import argparse
import codecs
import re
import os


class MyLex(object):
    """ """
    def __init__(self):
        """ """
        self.morph = pymorphy2.MorphAnalyzer()
        self.re_extract_words = re.compile(ur'[^a-zа-яё0-9-]')
        self.re_repeat_spaces = re.compile(ur'[ ]+')
        self.re_margin_spaces = re.compile(ur'(?:^[ ]+)|(?:[ ]+$)')
        # self.min_word_len = 3
        
    def extract_words(self, text):
        """ """
        text = re_extract_words.sub(u' ', text.lower())
        text = re_repeat_spaces.sub(u' ', text)
        text = re_margin_spaces.sub(u'' , text)
    
        words = re.split(ur' ', text)
        words = filter(lambda w: len(w) >= self.min_word_len, words)
        return  words

    def normalized_words(self, words):
        """ """
        doc_words = []
        for pos, word in enumerate(words):
            # if len(word) >= self.min_word_len:
            norm = self.morph.parse(word)[0].normal_form
            doc_words.append( (norm, word, pos) )
        return  doc_words

    def norm(self, word):
        """ """
        return  self.morph.parse(word)[0].normal_form


def parse_args():
    """
        -f  fib         = max_doc_id
        -s  s9          = 9 | something - useless
        
        -e  use_hashes  = True | None
        -w  work_folder = data
        -p  prefix      = povarenok1000

        -d  dat_name    = ./data/povarenok1000s_reduced_s.txt'
        -b  bin_name    = ./data/povarenok1000_backward.bin'
        -i  ndx_name    = ./data/povarenok1000_index.txt'
        -l  len_name    = ./data/povarenok1000_dlens.txt'

        -r  blk_rank    = './data/povarenok1000_black_rank.txt'
        -m  mrk_name    = 'C:\\data\\povarenok.ru\\all\\povarenok1000.tsv'
        -u  url_name    = 'C:\\data\\povarenok.ru\\1_1000\\urls.txt'
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-w', dest='folder', action='store', type=str,  default='data')
    parser.add_argument('-p', dest='prefix', action='store', type=str,  default='povarenok1000')

    parser.add_argument('-f', dest='fib', action='store', type=int,  default=0)
    parser.add_argument('-s', dest='s9',  action='store', type=int,  default=0)

    parser.add_argument('-e', dest='use_hashes', action='store_const', const=True)

    parser.add_argument('-d', dest='dat_name',   action='store', type=str,  default=None)
    parser.add_argument('-b', dest='bin_name',   action='store', type=str,  default=None)
    parser.add_argument('-i', dest='ndx_name',   action='store', type=str,  default=None)
    parser.add_argument('-l', dest='len_name',   action='store', type=str,  default=None)
    parser.add_argument('-r', dest='blk_rank',   action='store', type=str,  default=None)
    parser.add_argument('-m', dest='mrk_name',   action='store', type=str,  default='C:\\data\\povarenok.ru\\all\\povarenok1000.tsv')
    parser.add_argument('-u', dest='url_name',   action='store', type=str,  default='C:\\data\\povarenok.ru\\1_1000\\urls.txt')

    args = parser.parse_args()

    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    letter = ('f' if args.fib else ('s' if args.s9 else None))
    if not letter:  raise ValueError

    if args.prefix != 'povarenok1000' and not args.url_name:  raise ValueError

    if not args.dat_name: args.dat_name = (args.prefix + letter + '_' + 'reduced.txt')
    if not args.bin_name: args.bin_name = (args.prefix + letter + '_' + 'backward.bin')
    if not args.ndx_name: args.ndx_name = (args.prefix + letter + '_' + 'index.txt')
    if not args.len_name: args.len_name = (args.prefix + letter + '_' + 'dlens.txt')    
    if not args.blk_rank: args.blk_rank = (args.prefix + letter + '_' + 'black_rank.txt')

    args.dat_name = args.folder + '/' + args.dat_name 
    args.bin_name = args.folder + '/' + args.bin_name
    args.ndx_name = args.folder + '/' + args.ndx_name
    args.len_name = args.folder + '/' + args.len_name
    args.blk_rank = args.folder + '/' + args.blk_rank

    return args

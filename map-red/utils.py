﻿import pymorphy2
import argparse
# import hashlib
import codecs
import re
import os


class MyLex(object):
    """ """
    def __init__(self):
        """ """
        self.morph = pymorphy2.MorphAnalyzer()
        # self.hasher = hashlib.md5()
        self.hash_len = 251

        # self.min_word_len = 3
        self.re_extract_words = re.compile(ur'[^a-zа-яё0-9]')
        self.re_repeat_spaces = re.compile(ur'[ ]+')
        self.re_margin_spaces = re.compile(ur'(?:^[ ]+)|(?:[ ]+$)')
        
    def extract_words(self, text):
        """ """
        text = self.re_extract_words.sub(u' ', text.lower())
        text = self.re_repeat_spaces.sub(u' ', text)
        text = self.re_margin_spaces.sub(u'' , text)
    
        words = re.split(ur' ', text)
        # words = filter(lambda w: len(w) >= self.min_word_len, words)
        return  words

    def normalize(self, word):
        """ """
        # if len(word) >= self.min_word_len:
        norm = self.morph.parse(word)[0].normal_form

        # self.hasher.update(word.encode('utf-8'))
        # hash = int(self.hasher.hexdigest(), 16) % self.hash_len
        hash = sum(map(ord, word)) % self.hash_len
        
        return  (norm, hash)

    def norm(self, word):
        """ """
        return  self.morph.parse(word)[0].normal_form

    def incorrect_keyboard_layout(self, string, mode='2cyr'):
        """ Incorrect keyboard layout """
        dgt = u'1234567890 '
        lat = u'~`!@#$%^&qwertyuiop[]asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>? 1234567890'
        cyr = u'ёЁ!"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ, 1234567890'

        new_string = ""
        if   all(s in dgt for s in string):
            return string
        elif mode == '2cyr' and all(s in lat for s in string):
            for s in string:
                new_string += cyr[ lat.index(s) ]
        elif mode == '2lat' and all(s in cyr for s in string):
            for s in string:
                new_string += lat[ cyr.index(s) ]
        else: new_string = None
        return new_string

    def traslit(self, string, mode='2cyr'):
        return


def norm_url(url):
    return re.sub(r'^https?://(?:www\.|.*)?povarenok\.ru/|/?\r?\n?$', '', url)


def parse_args():
    """
        -f  fib        = max_doc_id
        -s  s9         = 9

        -e  use_hashes = True | None

        -d  dat_name   = './data/povarenok1000s_reduced_s.txt'
        -o  blk_rank   = './data/povarenok1000_ranked.txt'

        -b  bin_name   = './data/povarenok1000_backward.bin'
        -i  ndx_name   = './data/povarenok1000_index.txt'
        -l  len_name   = './data/povarenok1000_dlens.txt'

        -m  mrk_name   = 'C:\\data\\povarenok.ru\\all\\povarenok1000.tsv'
        -u  url_name   = 'C:\\data\\povarenok.ru\\1_1000\\urls.txt'
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', dest='fib', action='store', type=int,  default=0)
    parser.add_argument('-s', dest='s9',  action='store', type=int,  default=0)

    parser.add_argument('-e', dest='use_hashes', action='store_const', const=True)

    parser.add_argument('-d', dest='dat_name',   action='store', type=str,  default='./data/povarenok1000s_reduced_s.txt')
    parser.add_argument('-o', dest='rnk_name',   action='store', type=str,  default='./data/povarenok1000_ranked.txt')

    parser.add_argument('-b', dest='bin_name',   action='store', type=str,  default='./data/povarenok1000s_backward.bin')
    parser.add_argument('-i', dest='ndx_name',   action='store', type=str,  default='./data/povarenok1000_index.txt')
    parser.add_argument('-l', dest='len_name',   action='store', type=str,  default='./data/povarenok1000_dlens.txt')
    
    parser.add_argument('-m', dest='mrk_name',   action='store', type=str,  default='C:\\data\\povarenok.ru\\all\\povarenok1000.tsv')
    parser.add_argument('-u', dest='url_name',   action='store', type=str,  default='C:\\data\\povarenok.ru\\1_1000\\urls.txt')

    args = parser.parse_args()

    letter = ('f' if args.fib else ('s' if args.s9 else None))
    if not letter:  raise ValueError

    return args

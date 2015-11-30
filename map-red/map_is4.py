#!/usr/bin python
# -*- coding: utf-8 -*-

from base64 import b64decode
from zlib import decompress

import pymorphy2
import hashlib
import codecs
import sys
import re


import zipimport
importer = zipimport.zipimporter('bs123.zip')
bs4 = importer.load_module('bs4')


class MyLex(object):
    """ """
    def __init__(self):
        """ """
        self.morph = pymorphy2.MorphAnalyzer()
        self.hasher = hashlib.md5()
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

        self.hasher.update(word.encode('utf-8'))
        hash = int(self.hasher.hexdigest(), 16) % self.hash_len
        
        return  (norm, hash)


mylex = MyLex()
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for line in sys.stdin:
    splt = line.strip().split()

    if len(splt) == 2:
        id, doc = splt
        html = decompress(b64decode(doc))
    
        try:
            html = html.decode('utf8', 'ignore')
            bs = bs4.BeautifulSoup(html, 'html.parser')
            del html

            # kill all script and style elements
            for script in bs(["script", "style"]):
                script.extract() # rip it out
            text = u' '.join( bs.strings )
            del bs
        except: continue

        words = mylex.extract_words(text)
        del text
        if len(words) > 0:
            print u'$\t%06d\t%06d' % ( int(id), len(words) )

            for pos, word in enumerate(words):
                norm, hash = mylex.normalize(word)
                print u'%s\t%06d\t%06d\t%06d' % ( norm, int(id), int(pos), int(hash) )
        del words

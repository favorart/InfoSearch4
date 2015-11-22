import pymorphy2
import codecs
import re


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

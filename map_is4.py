#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64decode
from zlib import decompress

import codecs
import sys
import re


import zipimport
importer = zipimport.zipimporter('bs123.zip')
bs4 = importer.load_module('bs4')


sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
for line in sys.stdin:

    id, doc = line.strip().split()
    html = decompress(b64decode(doc))
    
    try:
        html = html.decode('utf8', 'ignore')
        bs = bs4.BeautifulSoup(html, 'html.parser')
        text = bs.get_text()
    except:
        continue
    
    text = re.sub(ur'[^a-zа-яё0-9-]',     ur' ', text.lower())
    text = re.sub(ur'[a-zа-яё0-9-]{1,2}', ur' ', text)
    text = re.sub(ur'[ ]+',               ur' ', text)

    words = text.split(u' ')
    # for word in [ w for w in list(set(words)) if len(w) > 2 ]:
    for pos,word in enumerate(words):
        print u'%s\t%s' % (word, id, pos) 


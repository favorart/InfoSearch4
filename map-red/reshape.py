#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64decode, b64encode
from itertools import groupby
from operator import itemgetter

import codecs
# import pprint
import json
import time
import sys
sys.path.insert(0, 'map-red')
sys.path.insert(0, '..')

import re
import os


def reshape(dat_name, ndx_name, bin_name, len_name, archiver,
            use_hashes=True, use_json=True, verbose=False, fib_archiver=None):
    """ Create the tree files:
        
        1. ( N_+_documents_lengthes )
        2. ( norm  offset  size_ids   [sizes_posits]   [sizes_hashes] )_concat-ed
        3. (backward_index_+_coords_+_hashes)_bin_archived_concat-ed
    """
    quantity = 0
    start_time = time.time()
    with open(bin_name, 'wb') as f_bin:
        with codecs.open(ndx_name, 'w', encoding='utf-8') as f_index:

            if use_json: print >>f_index, '{'
            with codecs.open(dat_name, 'r', encoding='utf-8') as f_data:
                for word, group in groupby( ( line.strip().split('\t') for line in f_data if len(line.split('\t', 1)[0]) ), key=itemgetter(0)):

                    if not (quantity % 100):
                        print >>sys.stderr, word.encode('cp866', 'ignore')
                    quantity += 1

                    word_tell = f_bin.tell()
                    id_parts = 0

                    pos, hss = [], []
                    index = {}
                    for g in group:
                        splt = g[1:]

                        # 1. ( N    documents lengthes )
                        if (len(splt) == 1) and (word == u'$'):
                            coded = splt[0]
                
                            start_time = time.time()
                            decoded = archiver.decode(b64decode(coded))
                            print '$ - %.3f sec.', (time.time() - start_time)
                            
                            N = decoded[0]/2
                            ids = decoded[1:N+1]
                            lens = decoded[N+1:]
                            
                            for i in xrange(1,len(ids)):
                                ids[i] += ids[i-1]
                            
                            with open(len_name, 'w') as f_dlen:
                                print >>f_dlen, '%d\t%s' % ( N, ' '.join([ '%d,%d' % (did, dlen)
                                                                          for did, dlen in zip(ids, lens) ]) ),
                            del coded, decoded

                        # 2. json( word : (offset,size) )
                        elif (len(splt) >= 2):

                            if   len(splt) > 2 and int(splt[0]) == 0:
                                id, id_part, ids_b64, lens_b64 = splt

                            elif len(splt) > 2 and use_hashes:
                                id, id_part, pos_b64, hss_b64 = splt

                            elif len(splt) > 1 and not use_hashes:
                                id, id_part, pos_b64 = splt

                            else:
                                raise Exception('NO WORD IDS!!! %s' % word)

                            if int(id) == 0:
                                if id_parts:
                                    # # создаём инвертированный список
                                    # decoded_ids = archiver.decode(coded_ids)
                                    # for 
                                    coded_ids1  = b64decode( ids_b64)
                                    coded_lens1 = b64decode(lens_b64)
                                    del ids_b64, lens_b64
                                else:
                                    # Получили все номера документов для данного слова
                                    coded_ids  = b64decode( ids_b64)
                                    coded_lens = b64decode(lens_b64)
                                    del ids_b64, lens_b64
                                id_parts += 1

                            else:
                                id = (int(id) - 1)
                                if use_hashes:
                                    coded_pos, coded_hss = b64decode(pos_b64), b64decode(hss_b64)
                                    pos.append(coded_pos)
                                    hss.append(coded_hss)
                                    
                                else:
                                    coded_pos = b64decode(pos_b64)
                                    pos.append(coded_pos)
                    
                    if word != '$':
                        # ('offset', 'size')
                        
                        # index['parts'] = id_parts
                        # Записываем их в бинарный файл первыми
                        if  id_parts > 1:
                            f_tell = f_bin.tell()
                            f_bin.write(coded_ids)
                            f_tell1 = f_bin.tell()
                            f_bin.write(coded_ids1)

                            index['ids']  = (f_tell, len(coded_ids), f_tell1, len(coded_ids1))
                            del coded_ids, coded_ids1

                            # Затем количества позиций для каждого документа
                            f_tell = f_bin.tell()
                            f_bin.write(coded_lens)
                            f_tell1 = f_bin.tell()
                            f_bin.write(coded_lens1)

                            index['lens'] = (f_tell, len(coded_lens), f_tell1, len(coded_lens1))
                            del coded_lens, coded_lens1
                        else:
                            index['ids']  = (f_bin.tell(), len(coded_ids))
                            f_bin.write(coded_ids)

                            # Затем количества позиций для каждого документа
                            index['lens'] = (f_bin.tell(), len(coded_lens))
                            f_bin.write(coded_lens)

                            del coded_ids, coded_lens

                        # Позиции
                        shifts1 = [ len(p) for p in pos ]
                        shifts2 = [ len(h) for h in hss ]

                        # if len(shifts1) != len(shifts2):
                        #     print "ERROR!!!"
                        #     sys.exit()

                        # coded  = archiver.code (shifts1)
                        # decoded = archiver.decode(coded)
                        # 
                        # if len(shifts1) != len(decoded):
                        #     print "DECODED LEN!!!"
                        #     print len(shifts1), len(decoded)
                        #     print word.encode('cp866', 'ignore')
                        #     sys.exit()
                        # 
                        # for i,s,d in zip(range(len(shifts1)), shifts1, decoded):
                        #     if s != d:
                        #         print "DECODED"; print i,s,d
                        #         print word.encode('cp866', 'ignore')
                        #         sys.exit()

                        # index['posits'] = (f_bin.tell(), b64encode(coded) )

                        index['posits'] = (f_bin.tell(), b64encode(archiver.code(shifts1)) )
                        # Записываем их в бинарный файл
                        for p in pos: f_bin.write(p)

                        # В конце хэши
                        # shifts = [ len(h) for h in hss ]

                        index['hashes'] = (f_bin.tell(), b64encode(archiver.code(shifts2)) )
                        # Записываем их в бинарный файл
                        for h in hss: f_bin.write(h)
                        # size = shifts[i+1] - shifts[i]

                        if use_json:
                            print >>f_index, '\t"%s" : ' % word
                            print >>f_index, json.dumps(index, sort_keys=True, indent=2,
                                                        ensure_ascii=False, encoding='utf-8'), ','
                        else:
                            print >>f_index, u'%s\t%s' % (word, u' '.join( u'%s,%d,%d' % (k,v[0],v[1]) if k in ["ids","lens"]
                                                                        else u'%s,%s' % (k,v)  for k,v in index.items()))
            if use_json: print >>f_index, '\n\n"" : [] }\n'

    with codecs.open('error.txt', 'a+', encoding='utf-8') as f_err:
        print >>f_err, "\n\n%d, %.3f sec" % (quantity, time.time() - start_time)
    return


import utils
import fib_archive
import s9_archive


if __name__ == '__main__':

    args = utils.parse_args()

    if   args.fib:
        archiver = fib_archive.FibonacciArchiver(args.fib)
    elif args.s9:
        archiver =  s9_archive.Simple9Archiver()

    reshape(args.dat_name, args.ndx_name, args.bin_name, args.len_name,
            archiver=archiver, use_hashes=args.use_hashes)


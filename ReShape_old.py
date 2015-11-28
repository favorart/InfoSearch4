#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64decode
from itertools import groupby
from operator import itemgetter

import pymorphy2
import argparse
import hashlib
import codecs
import pprint
import json
import sys
import os


import zipimport
importer = zipimport.zipimporter('bs123.zip')


def reshape(dat_name, ndx_name, bin_name, len_name, use_hashes=True, verbose=False):
    """ Create the tree files:
        
        1. ( N_+_documents_lengthes )
        2. ( norm  offset  size_ids   [sizes_posits]   [sizes_hashes] )_concat-ed
        3. (backward_index_+_coords_+_hashes)_bin_archived_concat-ed
    """
    with open(bin_name, 'wb') as f_bin:
        with codecs.open(ndx_name, 'w', encoding='utf-8') as f_index:
            with codecs.open(dat_name, 'r', encoding='utf-8') as f_data:

                print >>f_index, '{'
                for word, group in groupby((line.strip().split('\t') for line in f_data), key=itemgetter(0)):

                    word_ids = False
                    hss = []

                    if word != '$':
                        index = {}
                        print >>f_index, '\t"%s" : ' % word
                        gs = sorted(group, key=lambda x: int(x[1]))
                    else:
                        gs = group

                    for g in gs:
                        splt = g[1:] # .strip().split('\t')

                        # 1. ( N    documents lengthes )
                        if (len(splt) == 1) and (word == u'$'):
                            coded = splt[0]
                
                            decoded = archiver.decode(b64decode(coded))
                            with open(len_name, 'w') as f_dlen:
                                print >>f_dlen, '%d\t%s' % ( decoded[0], ' '.join([ str(d) for d in decoded[1:] ]) ),
            
                            del coded, decoded

                        # 2. json( word : (offset,size) )
                        elif (len(splt) >= 2):
                            if use_hashes and len(splt) > 2:
                                id, pos_coded, hss_coded = splt
                            elif int(splt[0]) == 0:
                                id, coded = splt
                            else:
                                raise Exception('NO WORD IDS!!!')

                            if int(id) == 0:
                                # Получили все номера документов для данного слова
                                coded_ids = b64decode(coded)
                                del coded

                                if verbose: print archiver.decode(coded_ids)
                                # Записываем их в бинарный файл первыми
                                # index['ids'] = [f_bin.tell(), len(coded_ids)]
                                # f_bin.write(coded_ids)
                                # del coded_ids
                                
                                # index['all_posits'] = [f_bin.tell(), 0]
                                
                                # index['posits'] = []
                                word_ids = True

                            elif not word_ids:
                                raise Exception('NO WORD IDS!!!')

                            else:
                                id = (int(id) - 1)
                                if use_hashes:
                                    coded_pos, coded_hss = b64decode(pos_coded), b64decode(hss_coded)
                                    hss.append(coded_hss)
                                else:
                                    coded_pos = b64decode(coded)
                                len_p = len(coded_pos)

                                # # if verbose: print archiver.decode(coded_pos)
                                pos.append(coded_pos)

                                # index['all_posits'][1] += len_p
                                # # index['posits'].append( (f_bin.tell(), len_p) )
                                
                                # f_bin.write(coded_pos)
                                # del coded_pos
                    
                    if word != '$':
                        # ('offset', 'size', 'n_coords')
                        index['ids'] = [f_bin.tell(), len(coded_ids), len(pos)]
                        f_bin.write(coded_ids)
                        del coded_ids

                        index['all_posits'] = [f_bin.tell(), sum([ len(p) for p in pos ])]
                        for p in pos: f_bin.write(p)

                        index['all_hashes'] = [f_bin.tell(), sum([ len(h) for h in hss ])]
                        # index['hashes'] = []
                        for h in hss:
                        #     index['hashes'].append( (f_bin.tell(), len(h)) )
                            f_bin.write(h)

                        print >>f_index, json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False, encoding='utf-8'), ','
                        # pprint.pprint(index, f_index, 1, -1)
                        # print >>f_index, ','
                print >>f_index, '\n\n"" : [] }\n'


if __name__ == '__main__':

    if not os.path.exists('data'):
        os.makedirs('data')

    parser = argparse.ArgumentParser() # description='Process some integers.'
    parser.add_argument('-f', dest='fib',        action='store', type=int,  default=0)
    parser.add_argument('-s', dest='s9',         action='store', type=int,  default=0)
    parser.add_argument('-u', dest='use_hashes', action='store', type=bool, default=True)
    parser.add_argument('-d', dest='dat_name',   action='store', type=str,  default='./data/povarenok1000s_reduced.txt')
    parser.add_argument('-b', dest='bin_name',   action='store', type=str,  default='./data/povarenok1000_backward.bin')
    parser.add_argument('-i', dest='ndx_name',   action='store', type=str,  default='./data/povarenok1000_index.txt')
    parser.add_argument('-l', dest='len_name',   action='store', type=str,  default='./data/povarenok1000_dlens.txt')

    args = parser.parse_args()

    #  if   (len(sys.argv) > 2 and sys.argv[1] == '-f'):
    if  args.fib:
        fib_archive = importer.load_module('fib_archive')
        archiver = fib_archive.FibonacciArchiver(args.fib)
        # all_docs= povarenok:199456, lenta:564548
        # max_number = int(sys.argv[2]) # max(199460, 564550)

    # elif (len(sys.argv) > 2 and sys.argv[1] == '-s'):
    elif args.s9:
        s9_archive = importer.load_module('s9_archive')
        archiver =  s9_archive.Simple9Archiver()

    else: raise ValueError

    # use_hashes =  args.use_hashes   # bool(sys.argv[3]) if len(sys.argv) > 3 else True

    # dat_name   = args.dat_name  # sys.argv[4] if len(sys.argv) > 4 else './data/povarenok1000s_reduced_s.txt'
    # bin_name   = args.bin_name  # sys.argv[5] if len(sys.argv) > 5 else './data/povarenok1000_backward.bin'
    # ndx_name   = args.ndx_name  # sys.argv[6] if len(sys.argv) > 6 else './data/povarenok1000_index.txt'
    # len_name   = args.len_name  # sys.argv[7] if len(sys.argv) > 7 else './data/povarenok1000_dlens.txt'

    reshape(args.dat_name, args.ndx_name, args.bin_name, args.len_name, use_hashes=args.use_hashes)


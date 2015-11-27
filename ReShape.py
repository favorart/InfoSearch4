#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64decode
from itertools import groupby
from operator import itemgetter

import pymorphy2
import hashlib
import codecs
import sys
import os


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


def reshape(dat_name, ndx_name, bin_name, len_name, use_hashes=True, verbose=False):
    """ Create the tree files:
        
        1. ( N_+_documents_lengthes )
        2. ( norm  offset  size_ids   [sizes_posits]   [sizes_hashes] )_concat-ed
        3. (backward_index_+_coords_+_hashes)_bin_archived_concat-ed
    """
    with open(bin_name, 'wb') as f_bin:
        with codecs.open(ndx_name, 'w', encoding='utf-8') as f_index:
            with codecs.open(dat_name, 'r', encoding='utf-8') as f_data:
                for word, group in groupby((line.strip().split('\t',1) for line in f_data), key=itemgetter(0)):
                # for line in f_data:

                    pos, hss = [], []
                    splt = [ g[1].strip().split('\t') for g in group ]

                    # 1. ( N_+_documents_lengthes )
                    if (len(splt) == 1) and (word == u'$'):
                        coded = splt
                
                        decoded = archiver.decode(b64decode(coded))
                        with open(len_name, 'w') as f_dlen:
                            print >>f_dlen, '%d\t%s' % ( decoded[0], ' '.join([ str(d) for d in decoded[1:] ]) )
            
                        del coded, decoded

                    # 2. ( norm  offset  size_ids   [sizes_posits]   [sizes_hashes] )
                    elif (len(splt) >= 3):
                        word, id, coded = splt

                        if int(id) == 0:
                            coded_ids = b64decode(coded)
                            del coded

                            if verbose: print archiver.decode(coded_ids)

                            print >>f_index, u'%s\t%s\t' % (word, f_bin.tell(), str(len(coded_ids))),
                            f_bin.write(coded_ids)
                            del coded_ids

                        else:
                            id = (int(id) - 1)
                            if use_hashes:
                                coded_pos, coded_hss = b64decode(coded[0]), b64decode(coded[1])
                                hss.append( (id, coded_hss) )
                            else:
                                coded_pos = b64decode(coded[0])
                            # if verbose: print archiver.decode(coded_pos)
                            pos.append( (id, coded_pos) )
                    
                    for coded_pos in pos:
                        print >>f_index, u'%s,%s' % ( f_bin.tell(), str(len(coded_pos)) )
                        f_bin.write(coded_pos)

                    if use_hashes:
                        print u'\t'
                        for coded_hss in hss:
                            print >>f_index, u'%s,%s' % ( f_bin.tell(), str(len(coded_hss)) )
                            f_bin.write(coded_hss)


if __name__ == '__main__':

    if not os.path.exists('data'):
        os.makedirs('data')

    use_hashes = bool(sys.argv[3]) if len(sys.argv) > 3 else True

    dat_name = sys.argv[4] if len(sys.argv) > 4 else './data/povarenok1000_reduced1.txt'
    bin_name = sys.argv[5] if len(sys.argv) > 5 else './data/povarenok1000_backward.bin'
    ndx_name = sys.argv[6] if len(sys.argv) > 6 else './data/povarenok1000_index.txt'
    len_name = sys.argv[7] if len(sys.argv) > 7 else './data/povarenok1000_dlens.txt'

    reshape(dat_name, ndx_name, bin_name, len_name, use_hashes=use_hashes)


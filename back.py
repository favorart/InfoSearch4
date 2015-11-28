
#     for line in f_index.readlines():
#         word, offset, size = line.strip().split()
#         self.w_offsets[word] = (offset, size)

# # print f_index>>, u'%s\t%d\t%d\t' % ( word, f_bin.tell(), len(coded_ids) ),
# f_index.write( u'%s\t%d\t%d' % ( word, f_bin.tell(), len(coded_ids) ) )

# # print f_index>>, u'%s\t%d\t%d\t' % ( word, f_bin.tell(), len(coded_ids) ),
# f_index.write( u'%s\t%d\t%d' % ( word, f_bin.tell(), len(coded_ids) ) )

## w1    ids_o1    ids_s1    pos_o1    poss_s1    po,ps po,ps .,.    hss_o1    hses_s1    ho,hs ho,hs .,.
## w2    ids_o2    ids_s2    pos_o2    poss_s2    po,ps po,ps .,.    hss_o2    hses_s2    ho,hs ho,hs .,.

## print >>f_index, '%d\t' % ( len(pos) ),
#f_index.write( u'\t%d\t%d\t' % (f_bin.tell(), size) )

#for coded_pos in pos:
#    # print >>f_index, u'%d,%d' % ( f_bin.tell(), len(coded_pos) ),
#    f_index.write( u' %d,%d' % (f_bin.tell(), len(coded_pos)) )
#    f_bin.write(coded_pos)

#if use_hashes:
#    size = sum([ len(h) for h in hss ])
#    # print >>f_index, u'\t%d\t' % len(hss)
#    f_index.write( u'\t%d\t%d\t' % (f_bin.tell(), size) )

#    for coded_hss in hss:
#        # print >>f_index, u'%d,%d' % ( f_bin.tell(), len(coded_hss) ),
#        f_index.write( u'%d,%d ' % (f_bin.tell(), len(coded_hss)) )
#        f_bin.write(coded_hss)

#f_index.write(u'\n')
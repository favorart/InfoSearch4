import sys
import codecs


flag_file = False
if not flag_file:
    sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    lines = sys.stdin.readlines()
    lines.sort()
    sys.stdout.write( u''.join(lines) )
else:
    fn_in  = 'data/povarenok1000_reduced.txt'
    fn_out = 'data/povarenok1000_reduced1.txt'
    
    with codecs.open(fn_in, 'r', encoding='utf-8') as f_red:
        lines = f_red.readlines()
    lines.sort()
    with codecs.open(fn_out, 'w', encoding='utf-8') as f_red2:
        f_red2.write( u''.join(lines) )
    


set INPUT=C:\data\povarenok.ru\1_1000\docs-000

type        %INPUT%.txt | python map_is4.py      | sort > .\data\mapped.txt
type  .\data\mapped.txt | python red_is4.py -s 9 | sort > .\data\output.txt

rem    type %INPUT%.txt | python map_is4.py      | sort | python red_is4.py -s 9 | sort > .\data\output_all.txt

type "C:\data\povarenok.ru\1_1000\docs-000.txt" | python map_is4.py      | sort > data\povarenok1000_mapped.txt
type             data\povarenok1000_mapped.txt  | python red_is4.py -s 9 | sort > data\povarenok1000_reduced.txt

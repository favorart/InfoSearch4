
set INPUT=C:\Users\MainUser\Downloads\Cloud.mail\povarenok.ru\1_1000\docs-000

type        %INPUT%.txt | python map_is4.py           | sort > .\data\mapped.txt
type  .\data\mapped.txt | python red_is4.py -f 564550 | sort > .\data\output.txt

rem    type %INPUT%.txt | python map_is4.py   | sort | python red_is4.py -s 0 | sort > .\data\output_all.txt

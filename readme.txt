-------------------------------------------------------------------------------------------
ЗАПУСК:

python TestMarks.py -s 9                                           # архиватор
                    -e                                             # использовать хэши
                    -i ..\all_index\povarenok_all_index.txt        # индекс обратного индекса
                    -b ..\all_index\povarenok_all_s_backward.bin   # обратный индекс
                    -l ..\all_index\povarenok_all_dlens.txt        # длины документов в обратном индексе
                    -u "C:\data\povarenok.ru\all\urls.txt"         # ссылки на документы в индексе
                    -m "C:\\data\\povarenok.ru\\all\\povarenok1000.tsv"
                  # выход
                    -o ..\all_index\povarenok_all_ranked.txt       # log проверки marks
-------------------------------------------------------------------------------------------
type data\povarenok.ru\1_1000\docs-*.txt | python map_is4.py      | python sort.py > data\povarenok1000_mapped_s.txt
type data\povarenok1000_mapped_s.txt     | python red_is4.py -s 9 | python sort.py > data\povarenok1000s_reduced_s.txt

python reshape.py -s 9                                             # архиватор
                  -e                                               # использовать хэши
                  -d data\povarenok_all_s_reduced_s.txt            # что преобразовывать
                # выход
                  -i ..\all_index\povarenok_all_index.txt          # индекс обратного индекса
                  -b ..\all_index\povarenok_all_s_backward.bin     # обратный индекс
                  -l ..\all_index\povarenok_all_dlens.txt          # длины документов в обратном индексе

hadoop: ./run_is4.sh
hadoop: ./run_sort.sh
-------------------------------------------------------------------------------------------
# map_is4.py, 'red_is4.py <-f <max>|-s 9>'

-f|-s - Фибоначчи или Simple9
#  Сжатию Фибоначчи нужно задать параметр -
#  максимальное число Фибоначчи, которые надо предподсчитать!
-------------------------------------------------------------------------------------------
flag | Значение по умолчанию
-------------------------------------------------------------------------------------------
-f   | *max_doc_id*
-s   | 9
-e   | *пусто*
-d   | './data/povarenok1000s_reduced_s.txt'
-o   | './data/povarenok1000_ranked.txt'  | 
-b   | './data/povarenok1000_backward.bin'
-i   | './data/povarenok1000_index.txt'
-l   | './data/povarenok1000_dlens.txt'  | 
-m   | 'C:\\data\\povarenok.ru\\all\\povarenok1000.tsv'
-u   | 'C:\\data\\povarenok.ru\\1_1000\\urls.txt'
-------------------------------------------------------------------------------------------
Files format:

dlens.txt:     N    id,len id,len ...
index.txt:     { norm : { "ids": [offset:size], "lens": [offset:size],
                          "posits": [offset,size,size,...], "hashes": [offset,size,size,...] }
backward.bin:  for one norm [ids] + [lens] + [posits] + [hashes]
-------------------------------------------------------------------------------------------



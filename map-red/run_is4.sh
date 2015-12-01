#!/bin/sh

# INPUT='/data/sites/povarenok.ru/1_1000/docs-000.txt'
# OUTPUT='is4_povarenok_1000_s_new'
INPUT='/data/sites/povarenok.ru/all/docs-*.txt'
OUTPUT='is4_povarenok_all_s_new'


hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name='InfoSearch4' \
    -file map_is4.py red_is4.py bs123.zip \
    -mapper  'python map_is4.py' \
    -reducer 'python red_is4.py -s 9' \
    -numReduceTasks 3 \
    -input ${INPUT} \
    -output ${OUTPUT}

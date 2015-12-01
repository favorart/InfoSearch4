#!/bin/sh

INPUT='/data/sites/povarenok.ru/all/docs-*.txt'
OUTPUT='is4_all_povarenok_new_map'

hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name='is4_map' \
    -file map_is4.py red_is4.py bs123.zip \
    -mapper  'python map_is4.py' \
    -input ${INPUT} \
    -output ${OUTPUT}

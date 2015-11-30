#!/bin/sh

# 1_10, 1_100, 1_1000
# INPUT='/data/sites/povarenok.ru/1_1000/docs-000.txt'
INPUT='/data/sites/povarenok.ru/all/docs-*.txt'
OUTPUT='infosearch4_povarenok'

hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.name='InfoSearch4' \
    -file map_is4.py red_is4.py bs123.zip \
    -mapper 'map_is4.py' \
    -reducer 'red_is4.py -s 9' \
    -numReduceTasks 3 \
    -input ${INPUT} \
    -output ${OUTPUT}

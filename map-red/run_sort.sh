#!/bin/sh

# INPUT='is4_all_povarenok_s_new/part-*'
# OUTPUT='is4_all_povarenok_s_new_s'
INPUT='is4_povarenok_1000_s_new/part-*'
OUTPUT='is4_povarenok_1000_s_new_s'


hadoop fs -rm -r ${OUTPUT}
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
        -D mapreduce.job.name='IS4_sort' \
        -file mapper.py red_sort.py \
        -mapper  'python mapper.py' \
        -reducer 'python red_sort.py' \
        -numReduceTasks 5 \
        -input ${INPUT} \
        -output ${OUTPUT}

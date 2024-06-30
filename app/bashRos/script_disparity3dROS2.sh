#!/bin/bash

while getopts i:p:s:m: flag
do
    case "${flag}" in
        i) info_topic=${OPTARG};;
        p) min_perc=${OPTARG};;
        s) steps_=${OPTARG};;
        m) max_distance=${OPTARG};;
    esac
done

source /home/gelbert2/source_ros22.bash
ros2 run disparity_3d disparity_to_3d --ros-args -p info_topic:=$info_topic -p min_perc:=$min_perc -p steps_:=$steps_ -p max_distance:=$max_distance
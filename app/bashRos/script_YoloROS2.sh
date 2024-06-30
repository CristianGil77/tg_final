#!/bin/bash

while getopts w:d:c:i:s:t: flag
do
    case "${flag}" in
        w) weights=${OPTARG};;
        d) data=${OPTARG};;
        c) confidence_threshold=${OPTARG};;
        i) iou_threshold=${OPTARG};;
        s) inference_size=${OPTARG};;
        t) input_image_topic=${OPTARG};;
    esac
done

source /home/gelbert2/source_ros22.bash
#ros2 run yolov5_ROS2 yolov5_node_timer --ros-args -p view_image:=False -p augment:=False -p timerp:=0.25
ros2 run yolov5_ROS2 yolov5_node_timer --ros-args -p view_image:=False -p augment:=False -p timerp:=0.25 -p weights:=$weights -p data:=$data -p confidence_threshold:=$confidence_threshold -p iou_threshold:=$iou_threshold -p inference_size_w:=$inference_size -p inference_size_h:=$inference_size -p input_image_topic:=$input_image_topic


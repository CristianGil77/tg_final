#!/bin/bash
source /home/gelbert2/source_ros1.bash
source /home/gelbert2/source_ros22.bash
source /home/gelbert2/bridge_ws/install/local_setup.bash
export ROS_MASTER_URI=http://localhost:11311
ros2 run ros1_bridge dynamic_bridge


import os
import time
import signal
import subprocess
from subprocess import Popen, PIPE

import logging
logging.basicConfig(level=logging.DEBUG)

from app.yaml import WriteYaml

import pathlib


class RosCaller:
    def __init__(self):
        self.bash_cmds_ros1 = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_plannertROS1.sh"
        ]
        self.bash_cmds_ros2 = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_IsaacROS2.sh"
        ]

        self.p_ros1 = None
        self.p_ros2 = None

        self.yaml = WriteYaml()
        self.path = str(pathlib.Path(__file__).parent.resolve())+'/'
        logging.info("path")
        logging.info(self.path)
    
    def start(self, opcion_jk):
        logging.info("opcion")
        logging.info(opcion_jk)


        fileName = "config/yolov5/yolov5_params.yaml"
        bool_acces, dict_params = self.yaml.yaml_to_dict_general(fileName, parents=True)
        print(dict_params)



        self.p_ros1 = 2
        self.p_ros2 = 5
        #logging.info(self.p_ros1.pid)
        self.p_ros15 = subprocess.run(["ls", "-l"], shell=True)



    def stop(self):
        logging.info("STOOP")
        # wait for the new process to finish
        #logging.info(self.p_ros1.pid)
        #os.killpg(os.getpgid(self.p_ros1.pid), signal.SIGTERM)
        if self.p_ros1 is not None:
            logging.info("ROS1111")
        if self.p_ros2 is not None:
            logging.info("ROS222")


import os
import time
import signal
import subprocess
from subprocess import Popen, PIPE

import logging
logging.basicConfig(level=logging.DEBUG)

from app.yaml import WriteYaml

import pathlib
import numpy as np




class RosCaller:
    def __init__(self):
        self.bash_cmds_ros1_main = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_objROS1.sh"
        ]

        self.bash_cmds_ros2_isaac = [
                "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_IsaacROS2.sh"
            ]

        self.bash_cmds_ros2_isaac_hist = [
                "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_IsaacHistROS2.sh"
            ]
            
        self.bash_cmds_ros2_disp3d = [
                "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_disparity3dROS2.sh"
            ]
        self.bash_cmds_ros2_yolo = [
                "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_YoloROS2.sh"
            ]

            
        self.bash_tf_static = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_tf_staticROS1.sh"
        ]
        self.bash_tf_broadcast = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_tf_imuROS1.sh"
        ]

        
        self.bash_camera_alert = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_cameralertROS1.sh"
        ]

        self.bash_stop_ros1 = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_stopROS1.sh"
        ]
        self.bash_stop_ros2 = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_stopROS2.sh"
        ]

        self.bash_simple = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_simpleROS1.sh"
        ]
        self.bash_bridge = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_bridge.sh"
        ]
        self.bash_aux = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_auxROS1.sh"
        ]
        
        self.bash_bluetooth = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_bluetooth.sh"
        ]
        
        self.bash_apaga = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_apagandose.sh"
        ]
        self.bash_saludo = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_saludo.sh"
        ]
        self.bash_saludo2 = [
            "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_saludo2.sh"
        ]

        self.p_bluetooth = None

        self.p_saludo = None

        self.p_ros1_main = None
        self.p_ros2_isaac = None
        self.p_ros2_disp3d = None
        self.p_ros2_yolo = None

        self.p_simple= None
        self.p_bridge = None
        self.p_aux = None
        
        self.p_tf_static = None
        self.p_tf_imu = None  

        self.p_camera_alert = None      

        self.bool_yolo, self.dict_yolo = None, None

        self.yaml = WriteYaml()
        self.path = str(pathlib.Path(__file__).parent.resolve())+'/'
        logging.info("path")
        logging.info(self.path)

    def initCommands(self, opcion_jk, use_imu_bool):

        if use_imu_bool:
            if opcion_jk == 1:
                self.bash_cmds_ros1_main = [
                    "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_objROS1_imu.sh"
                ]
            else:
                self.bash_cmds_ros1_main = [
                    "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_plannertROS1_imu.sh"
                ]
        else:
            if opcion_jk == 1:
                self.bash_cmds_ros1_main = [
                    "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_objROS1.sh"
                ]
            else:
                self.bash_cmds_ros1_main = [
                    "/home/gelbert2/Documents/Gelbert/Gelbert/app/bashRos/script_plannertROS1.sh"
                ]
    
    def load_dicts(self):

        #common
        fileName = "config/common/common.yaml"
        self.bool_common, self.dict_common = self.yaml.yaml_to_dict_general(fileName, parents=False)
       
        #Isaac
        fileName = "config/isaac/isaac_params.yaml"
        self.bool_isaac, self.dict_isaac = self.yaml.yaml_to_dict_general(fileName, parents=True)

        #preprocess
        fileName = "config/preprocess_node/preprocess_params.yaml"
        self.bool_prepro, self.dict_prepro = self.yaml.yaml_to_dict_general(fileName, parents=True)
       
        #YOLO ROS2
        fileName = "config/yolov5/yolov5_params.yaml"
        self.bool_yolo, self.dict_yolo = self.yaml.yaml_to_dict_general(fileName, parents=True)
        
        #Planner
        fileName = "config/local_planner/params.yaml"
        self.bool_planner, self.dict_planner = self.yaml.yaml_to_dict_general(fileName, parents=False)
        

    def calculate_steps(self, user_height):
        steps_ = (0.129+0.186)*user_height
        base = 0.05

        steps_ = np.floor(steps_/base)*base

        return steps_
    
    def calculate_height(self, user_height):

        maxh = user_height*(0.10588)
        minh = user_height*(0.15717)*(-1)

        return maxh, minh

    def start(self, opcion_jk):

        self.stop()

        self.load_dicts()

        use_imu_bool = str(self.dict_common["use_imu"]).lower() in ['true']

        
        self.initCommands(opcion_jk, use_imu_bool)
        
        

        #Start Bluetooth
        if self.bool_common:
            aux_str =  [" -b "+str(self.dict_common["bluetooth_addres"])]
        else:
            aux_str =  [" -b "+'00:42:79:3F:D8:8F']

        self.p_bluetooth = Popen(['bash', '-c', ' '.join(self.bash_bluetooth+aux_str)], stdout=PIPE, preexec_fn=os.setsid)
        self.p_bluetooth.communicate()
        
        logging.info(aux_str)
        # ---- #
        
        #Start Isaac
        if str(self.dict_prepro["use_hist_equ"]).lower() in ['true']:
            self.p_ros2_isaac = Popen(['bash', '-c', '&&'.join(self.bash_cmds_ros2_isaac_hist)], stdout=PIPE, preexec_fn=os.setsid)
        else:
            self.p_ros2_isaac = Popen(['bash', '-c', '&&'.join(self.bash_cmds_ros2_isaac)], stdout=PIPE, preexec_fn=os.setsid)
        # ---- #


        #Start audio ROS1 and bridge
        self.p_simple = Popen(['bash','-c', '&&'.join(self.bash_simple)], stdout=PIPE, preexec_fn=os.setsid)
        time.sleep(3)
        self.p_bridge = Popen(['bash','-c', '&&'.join(self.bash_bridge)], stdout=PIPE, preexec_fn=os.setsid)
        time.sleep(10)

        self.continue_(opcion_jk)
    
    def continue_(self, opcion_jk):

        if str(self.dict_common["use_steps"]).lower() in ['true']:
            steps_ = self.dict_common["steps"]
        else:
            steps_ = self.calculate_steps(self.dict_common["user_height"])

        maxh, minh = self.calculate_height(self.dict_common["user_height"])

        self.yaml.save_costmap(steps_, maxh, minh)


        if opcion_jk == 1:
            
            #Start YOLO ROS2
            if self.bool_yolo:
                aux_str =  [" -w "+self.dict_yolo["weights"]+" -d "+self.dict_yolo["data"]+" -c "+self.dict_yolo["confidence_threshold"]+" -i "+self.dict_yolo["iou_threshold"]+" -s "+self.dict_yolo["inference_size_"]+" -t "+self.dict_yolo["input_image_topic"]]
            else:
                aux_str =  [" -w "+'Yolov5_S_subi4Uv_pto_22.engine'+" -d "+'data.yaml'+" -c "+"0.3"+" -i "+"0.45"+" -s "+"416"+" -t "+"/zedm/zed_node/left/image_rect_color"]

            
            self.p_ros2_yolo = Popen(['bash', '-c', ' '.join(self.bash_cmds_ros2_yolo+aux_str)], stdout=PIPE, preexec_fn=os.setsid)
            time.sleep(3)
            # ---- #

            #Start aux and wait
            self.p_aux = Popen(['bash', '-c', '&&'.join(self.bash_aux)], stdout=PIPE, preexec_fn=os.setsid)
            
            self.p_aux.communicate()
            #logging.info("continue")
            # ---- #
            
            #Start disparity3d ROS2
            if (self.bool_isaac) and (self.bool_common) and (self.bool_planner):
                
                aux_str =  [" -i "+self.dict_isaac["left_camera_info_topic"]+" -p "+str(self.dict_isaac["min_perc"])+" -s "+str(steps_)+" -m "+str(self.dict_planner["Maximun_distance"])]
            else:
                aux_str =  [" -i "+'/zedm/zed_node/left/camera_info'+" -p "+'0.2'+" -s "+"0.5"+" -m "+"3.0"]

            #logging.info(aux_str)
            self.p_ros2_disp3d = Popen(['bash', '-c', ' '.join(self.bash_cmds_ros2_disp3d+aux_str)], stdout=PIPE, preexec_fn=os.setsid)
            time.sleep(3)

        #Start TF
        if str(self.dict_common["use_imu"]).lower() in ['true']:
            self.p_tf_imu = Popen(['bash', '-c', '&&'.join(self.bash_tf_broadcast)], stdout=PIPE, preexec_fn=os.setsid)
            time.sleep(30)
            self.p_saludo = Popen(['bash', '-c', '&&'.join(self.bash_saludo)], stdout=PIPE, preexec_fn=os.setsid)
            self.p_saludo.communicate()
        else:
            self.p_tf_static = Popen(['bash', '-c', '&&'.join(self.bash_tf_static)], stdout=PIPE, preexec_fn=os.setsid)
        
        #Start planner ROS1 or Obs
        self.p_ros1_main = Popen(['bash','-c', '&&'.join(self.bash_cmds_ros1_main)], stdout=PIPE, preexec_fn=os.setsid)
        time.sleep(3)

        
        
        self.p_saludo = Popen(['bash', '-c', '&&'.join(self.bash_saludo2)], stdout=PIPE, preexec_fn=os.setsid)
        self.p_saludo.communicate()

        time.sleep(30)
        self.p_camera_alert =Popen(['bash','-c', '&&'.join(self.bash_camera_alert)], stdout=PIPE, preexec_fn=os.setsid)




    def stop(self):
        #logging.info("STOOP")
        self.p_saludo = Popen(['bash', '-c', '&&'.join(self.bash_apaga)], stdout=PIPE, preexec_fn=os.setsid)
        self.p_saludo.communicate()

        time.sleep(5)

        
        self.stop_ros2()       
        self.stop_ros1()
        self.stop_simple() 
        self.stop_bridge()
    
    def stop_bridge(self):

        if self.p_bridge is not None:
            #logging.info("BRIDGE")
            os.killpg(os.getpgid(self.p_bridge.pid), signal.SIGTERM)

            #logging.info("STOOP BRIDGE")
    
    def stop_simple(self):

        if self.p_simple is not None:
            #logging.info("p_simple")
            os.killpg(os.getpgid(self.p_simple.pid), signal.SIGTERM)

            #logging.info("STOOP p_simple")


    
    
    def stop_ros1(self):
        

        if self.p_tf_static is not None:
            os.killpg(os.getpgid(self.p_tf_static.pid), signal.SIGTERM)

        if self.p_tf_imu is not None:
            os.killpg(os.getpgid(self.p_tf_imu.pid), signal.SIGTERM)

        if self.p_camera_alert is not None:
            os.killpg(os.getpgid(self.p_camera_alert.pid), signal.SIGTERM)


        if self.p_ros1_main is not None:
            os.killpg(os.getpgid(self.p_ros1_main.pid), signal.SIGTERM)
            #logging.info("ROS1111")

            p = Popen(['bash','-c', '&&'.join(self.bash_stop_ros1)], stdout=PIPE, preexec_fn=os.setsid)
            p.communicate()

            subprocess.run(['killall', '-9', 'rosmaster'])
            #logging.info("STOOP ROS")
        else:
            #logging.info("STOOP ROS?")

            p = Popen(['bash','-c', '&&'.join(self.bash_stop_ros1)], stdout=PIPE, preexec_fn=os.setsid)
            p.communicate()
            subprocess.run(['killall', '-9', 'rosmaster'])
    
    def stop_ros2(self):

        if self.p_ros2_disp3d is not None:
            #logging.info("DISPARITY")
            os.killpg(os.getpgid(self.p_ros2_disp3d.pid), signal.SIGTERM)

            #logging.info("STOOP DISPARITY")

        if self.p_ros2_yolo is not None:
            #logging.info("YOLO")
            os.killpg(os.getpgid(self.p_ros2_yolo.pid), signal.SIGTERM)

            #logging.info("STOOP YOLO")

            

        if self.p_ros2_isaac is not None:
            #logging.info("ROS220")
            os.killpg(os.getpgid(self.p_ros2_isaac.pid), signal.SIGTERM)

            p = Popen(['bash','-c', '&&'.join(self.bash_stop_ros2)], stdout=PIPE, preexec_fn=os.setsid)
            p.communicate()

            #logging.info("STOOP ROS2")
        else:
            #logging.info("STOOP ROS2?")

            p = Popen(['bash','-c', '&&'.join(self.bash_stop_ros2)], stdout=PIPE, preexec_fn=os.setsid)
            p.communicate()

    
    def shutdownall(self):
        subprocess.run(['shutdown', 'now'])



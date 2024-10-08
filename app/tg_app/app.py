import sys
import numpy as np
import pyzed.sl as sl
import cv2
import math
import collections
import tensorrt as trt
import os
import open3d as o3d
import time
from playsound import playsound
from adquisition import ZEDCamera
from preprocessing import Preprocessing
from Position import Ubication
from Inference import YOLOv5, ExpertCommittee
from audio import DirectionalAudioGenerator as AudioGenerator
from gui_yaml import WriteYaml

sys.path.append('app/tg_app/Inference/yolov8_cpp/build')
import yolo_module as YOLOv8
import threading


audio_playing = False

def play_audio_in_background(audio_feedback):
    global audio_playing
    audio_playing = True
    audio_feedback.play_audio()
    audio_playing = False


def main():

    print("Iniciando dispositivo")
    playsound("app/tg_app/audio/audios/iniciando_dispositivo.wav")


    clases = ["cama","rama","silla","puerta", "florero","persona","escalera","mesa",
         "basurero", "lampara de techo","candelabro","lampara de pared", "objeto desconocido"]



    miyaml = WriteYaml()

     #common
    fileName = "app/config/common/common.yaml"
    _, dict_common = miyaml.yaml_to_dict_general(fileName, parents=False)
    print("############################################")
    print("Configuraciones basicas:")
    print(dict_common)
    factor = dict_common["steps"] #0.39
    person_height = dict_common["user_height"] #1.77
    use_imu = dict_common["use_imu"]# True
    feedback_mode = dict_common["feedback_mode"]#1
    bluetooth_addres = dict_common["bluetooth_addres"]#None
    audio_speed = dict_common["audio_speed"]#1.0

     #Local planer
    fileName = "app/config/local_planner/params.yaml"
    _, dict_planer = miyaml.yaml_to_dict_general(fileName, parents=False)
    max_distance = dict_planer["Maximun_distance"]#10
    min_distance = 0.1

    #Yolov8
    fileName = "app/config/yolov5/yolov5_params.yaml"
    _, dict_yolo = miyaml.yaml_to_dict_general(fileName, parents=False)
    print("Configuraciones YOLO V8:")
    print(dict_yolo)
    engine_file_path = "app/tg_app/Inference/yolov8_cpp/" + dict_yolo["weights"] #"Inference/yolov8_cpp/y8_416.engine"
    #print(engine_file_path)
    t_size = dict_yolo["inference_size_"]#(416, 416)
    size = (t_size,t_size)
    num_labels = 12
    topk = dict_yolo["topk"]#100
    score_thres = dict_yolo["confidence_threshold"]#0.3
    iou_thres = dict_yolo["iou_threshold"]#0.45

    #preproces
    fileName = "app/config/preprocess_node/preprocess_params.yaml"
    _, dict_prepro = miyaml.yaml_to_dict_general(fileName, parents=False)
    print("Configuraciones preprocesamiento")
    print(dict_prepro)
    blur_threshold = dict_prepro["blur_threshold"]# 100.0
    clahe_clip_limit = dict_prepro["clahe_clip_limit"]#2.0
    clahe_t = dict_prepro["clahe_tile_grid_size"]
    clahe_tile_grid_size = (clahe_t,clahe_t)#(8, 8)
    angle = dict_prepro["max_angle"]
    yaw_angle_min = -angle
    yaw_angle_max = angle
    use_blur = dict_prepro["use_blur_filter"]
    use_hist_eq = dict_prepro["use_hist_equ"]
    use_clahe = dict_prepro["use_clahe"]

    #camara
    fileName = "app/config/zed_wrapper/common.yaml"
    _, dict_zed = miyaml.yaml_to_dict_general(fileName, parents=False)
    print("Configuraciones cámara ZED")
    print(dict_zed)

    ## Resolucion
    if dict_zed["resolution"]==0:
        resolution = sl.RESOLUTION.HD2K
    elif dict_zed["resolution"]==1:
        resolution = sl.RESOLUTION.HD1080
    elif dict_zed["resolution"]==2:
        resolution = sl.RESOLUTION.HD720
    elif dict_zed["resolution"]==3:
        resolution = sl.RESOLUTION.VGA

    ## Calidad de la nube de puntos
    if dict_zed["quality"]==1:
        depth_mode = sl.DEPTH_MODE.PERFORMANCE
    elif dict_zed["quality"]==2:
        depth_mode = sl.DEPTH_MODE.QUALITY
    elif dict_zed["quality"]==3:
        depth_mode = sl.DEPTH_MODE.ULTRA
    elif dict_zed["quality"]==4:
        depth_mode = sl.DEPTH_MODE.NEURAL

    ##Modo de sensado
    if dict_zed["sensing_mode"]==0:
        sensing_mode = sl.SENSING_MODE.STANDARD
    elif dict_zed["sensing_mode"]==1:
        sensing_mode = sl.SENSING_MODE.FILL
   
    deque_maxlen = 3
    distance_variation_threshold = 1
    min_class_count = 2
    max_distance_audio = 3
       
    # Inicialización de objetos con parámetros configurables
    zed_camera = ZEDCamera(resolution, depth_mode, sensing_mode, max_distance, min_distance)
    preprocessing = Preprocessing(blur_threshold, clahe_clip_limit, clahe_tile_grid_size, yaw_angle_min, yaw_angle_max)
    model = YOLOv8.YOLOv8Wrapper(engine_file_path, size, num_labels, topk, score_thres, iou_thres)
    expert_committee = ExpertCommittee(maxlen=deque_maxlen, distance_variation_threshold=distance_variation_threshold, min_class_count=min_class_count)
    relative_position = Ubication(person_height, factor)
    audio_feedback = AudioGenerator(clases, max_distance=max_distance_audio, feedback_mode=feedback_mode, audio_speed = audio_speed, angle = angle)

    print("Aplicativo listo")
    playsound("app/tg_app/audio/audios/aplicativo_listo.wav")

    while True:
        # Captura de datos de la cámara ZED
        err = zed_camera.zed.grab(zed_camera.runtime_params)
        if err == sl.ERROR_CODE.SUCCESS:
            ###############################################################################
            # Obtener fotogramas y generar nube de puntos
            image_ocv = zed_camera.capture_image()
            point_cloud = zed_camera.capture_point_cloud()
            

            ###############################################################################
            # Preprocesamiento

            if use_blur == True:
                if preprocessing.detect_blur(image_ocv):
                    continue
            if use_hist_eq == True:
                image_ocv = preprocessing.equalize_histogram(image_ocv)
            elif use_clahe == True:
                image_ocv = preprocessing.apply_clahe(image_ocv)

            #preprocess_image = preprocessing.apply_clahe(image_ocv)

            ###############################################################################
            # Detecciones
            detections = model.process_frame(image_ocv)

            if detections:
                ###############################################################################
                # Posicion relativa
                relative_position.calculate_ubication(detections, point_cloud, image_ocv)
                
                ###############################################################################
                # Realimentacion audio
                sorted_detections = sorted(detections, key=lambda x: x['distance'])
                if sorted_detections[0]['distance'] < 3.5:
                    audio_feedback.generate_final_audio(sorted_detections[0], velocidad= audio_speed)
                    if not audio_playing:
                        print("audio ········································································")
                        audio_thread = threading.Thread(target=play_audio_in_background, args=(audio_feedback,))
                        audio_thread.start()
                #relative_position.draw_bboxes(image_ocv, detections, clases )

            
            #cv2.imshow('YOLOv8 Detections', image_ocv)
            if cv2.waitKey(30) >= 0:
                break
        else:
            # Si la cámara no está conectada, reproduce audio y espera 15 segundos
            print("Cámara desconectada, reproduciendo alerta...")
            playsound("app/tg_app/audio/audios/camara_desconectada.wav")
            time.sleep(15)
            continue  # Reinicia el bucle

    # Limpieza y cierre
    cv2.destroyAllWindows()
    zed_camera.zed.close()

if __name__ == "__main__":
    main()


import cv2
import torch
from pathlib import Path
import sys
import collections
import copy
#sys.path.append('Inference/JetsonYolov5') # add yolov5/ to path


# import imutils
# from yoloDet import YoloTRT

class YOLOv5:
    def __init__(self):
        # Cargar el modelo
        self.model = YoloTRT(library="Inference/JetsonYolov5/yolov5/build/libmyplugins.so", engine="Inference/JetsonYolov5/yolov5/build/yolov5s.engine", conf=0.5, yolo_ver="v5")


    def detect(self, image):
        detections, t = self.model.Inference(image)

        return detections

    
class ExpertCommittee:
    def __init__(self, maxlen=3, distance_variation_threshold=1, min_class_count=2):
        """
        Inicializa la clase ExpertCommittee con un deque de longitud máxima,
        un umbral de variación de distancia y un umbral de detecciones mínimas por clase.

        :param maxlen: Longitud máxima del deque.
        :param distance_variation_threshold: Umbral de variación de distancia.
        :param min_class_count: Umbral de detecciones mínimas por clase.
        """
        self.detection_deque = collections.deque(maxlen=maxlen)
        self.distance_variation_threshold = distance_variation_threshold
        self.min_class_count = min_class_count

    def update_detections(self, yolo_detections):
        """
        Actualiza el deque con nuevas detecciones y selecciona el diccionario más confiable.

        :param yolo_detections: Lista de diccionarios con las detecciones de YOLO, incluyendo clase, bbox, probabilidad, distancia y ángulo.
        :return: El diccionario elegido que cumple con los criterios especificados, o None si no se cumple ningún criterio.
        """
        # Ordena las detecciones por distancia (la menor distancia primero)
        sorted_detections = sorted(yolo_detections, key=lambda x: x['distance'])

        print("·······················todas las detecciones····································")
        print(sorted_detections)
        print("································seleccionadas·····································")

        # Selecciona la detección con la menor distancia y añádela al deque
        self.detection_deque.append(sorted_detections[0])
        print(self.detection_deque)

        # Si el deque está lleno, revisa los criterios de selección
        if len(self.detection_deque) == self.detection_deque.maxlen:
            class_counts = {}
            for detection in self.detection_deque:
                class_name = detection['class']
                if class_name not in class_counts:
                    class_counts[class_name] = []
                class_counts[class_name].append(detection)

            for class_name, detections in class_counts.items():
                if len(detections) >= self.min_class_count:
                    distances = [d['distance'] for d in detections]
                    if max(distances) - min(distances) <= self.distance_variation_threshold:
                        # Encuentra el diccionario con la distancia mínima
                        min_distance_detection = min(detections, key=lambda d: d['distance'])
                        return min_distance_detection

            # Si ninguna clase se repite al menos min_class_count veces pero las distancias varían menos del umbral
            all_distances = [d['distance'] for d in self.detection_deque]
            if max(all_distances) - min(all_distances) <= self.distance_variation_threshold:
                min_distance_detection = min(self.detection_deque, key=lambda d: d['distance'])
                # Crea una copia del diccionario y cambia la clase a 'desconocido'
                result = copy.deepcopy(min_distance_detection)
                result['class'] = 12#'desconocido'
                return result

        return None

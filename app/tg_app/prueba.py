import collections
import random
import time
import copy

class YOLOExpertCommittee:
    def __init__(self, maxlen=3):
        """
        Inicializa la clase YOLOExpertCommittee con un deque de longitud máxima.

        :param maxlen: Longitud máxima del deque.
        """
        self.detection_deque = collections.deque(maxlen=maxlen)

    def update_detections(self, yolo_detections):
        """
        Actualiza el deque con nuevas detecciones y selecciona el diccionario más confiable.

        :param yolo_detections: Lista de diccionarios con las detecciones de YOLO, incluyendo clase, bbox, probabilidad, distancia y ángulo.
        :return: El diccionario elegido que cumple con los criterios especificados, o None si no se cumple ningún criterio.
        """
        # Ordena las detecciones por distancia (la menor distancia primero)
        sorted_detections = sorted(yolo_detections, key=lambda x: x['distance'])

        # Selecciona la detección con la menor distancia y añádela al deque
        self.detection_deque.append(sorted_detections[0])

        print(self.detection_deque)
        print("=======================================================================================")

        # Si el deque está lleno, revisa los criterios de selección
        if len(self.detection_deque) == self.detection_deque.maxlen:
            class_counts = {}
            for detection in self.detection_deque:
                class_name = detection['class']
                if class_name not in class_counts:
                    class_counts[class_name] = []
                class_counts[class_name].append(detection)

            for class_name, detections in class_counts.items():
                if len(detections) >= 2:
                    distances = [d['distance'] for d in detections]
                    if max(distances) - min(distances) <= 1:
                        # Encuentra el diccionario con la distancia mínima
                        min_distance_detection = min(detections, key=lambda d: d['distance'])
                        print("==================================clase elegida============================")
                        return min_distance_detection
                    
            # Si ninguna clase se repite al menos 2 veces pero las distancias varían menos de 1 metro
            all_distances = [d['distance'] for d in self.detection_deque]
            if max(all_distances) - min(all_distances) <= 1:
                print("===================desconocido=============================================")
                min_distance_detection = min(self.detection_deque, key=lambda d: d['distance'])
                result = copy.deepcopy(min_distance_detection)
                result['class'] = 'desconocido'
                return result

        return None

# Ejemplo de simulación de uso continuo
def simulate_yolo_detections():
    """
    Simula la generación continua de detecciones de YOLO.
    """
    classes = ["car", "motorbike", "person"]
    while True:
        # Simular detecciones de YOLO con valores aleatorios
        yolo_detections = [
            {"class": random.choice(classes), "bbox": [100, 200, 150, 250], "probability": random.uniform(0.8, 1.0), "distance": random.uniform(0.5, 3.0), "angle": random.uniform(0, 180)},
            {"class": random.choice(classes), "bbox": [120, 220, 160, 270], "probability": random.uniform(0.8, 1.0), "distance": random.uniform(0.5, 3.0), "angle": random.uniform(0, 180)},
            {"class": random.choice(classes), "bbox": [130, 230, 170, 280], "probability": random.uniform(0.8, 1.0), "distance": random.uniform(0.5, 3.0), "angle": random.uniform(0, 180)},
        ]
        yield yolo_detections

committee = YOLOExpertCommittee()

# Simular un bucle continuo donde se procesan los fotogramas
for yolo_detections in simulate_yolo_detections():

    print(yolo_detections)
    chosen_detection = committee.update_detections(yolo_detections)
    if chosen_detection:
        print(f"Detección elegida: {chosen_detection}")
    # Simula un retraso entre fotogramas
    time.sleep(1)

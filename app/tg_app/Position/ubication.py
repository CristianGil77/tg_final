import numpy as np
import cv2
import pandas as pd
import os


class Ubication:
    def __init__(self, person_height, factor=0.289):
        """
        Inicializa la clase Ubication con el factor de escala, la altura de la persona y umbrales de distancia y ángulo.

        :param factor: Factor de escala para las distancias.
        :param person_height: Altura de la persona en metros.
        """
        self.factor = factor
        self.person_height = person_height
        self.length_step = person_height * factor

    def calculate_ubication(self, detections, point_cloud, image):
        """
        Calcula la distancia y el ángulo para cada detección y dibuja esta información en la imagen.

        :param detections: Lista de detecciones con coordenadas del bounding box.
        :param point_cloud: Nube de puntos en un array numpy.
        :param shape: Forma de la nube de puntos (altura, ancho, canales).
        :param image: Imagen en la que se dibujarán los resultados.
        """
        for detection in detections:
            distance, point = self.calcular_distancia_mediana(point_cloud, detection['bbox'])
            if point is not None:
                angle_degrees = self._calculate_angle(point)
                detection['distance'] = distance
                detection['angle'] = angle_degrees
                # self.draw_ubication(image, distance, angle_degrees, x, y)
            else:
                detection['distance'] = None
                detection['angle'] = None

            #self.draw_ubication(image, distance, angle_degrees, x, y)

    def calcular_distancia_mediana(self, point_cloud, bbox):
        x_min, y_min, width, height = map(int, bbox)
        x_max = x_min + width
        y_max = y_min + height

        # Calcular el centro del bounding box original
        x_centro = (x_min + x_max) / 2.0
        y_centro = (y_min + y_max) / 2.0

        # Calcular las nuevas dimensiones para encoger el bounding box al 50%
        nuevo_ancho = width * 0.75
        nuevo_alto = height * 0.75

        # Calcular los nuevos límites del bounding box
        nuevo_x_min = int(x_centro - nuevo_ancho / 2.0)
        nuevo_x_max = int(x_centro + nuevo_ancho / 2.0)
        nuevo_y_min = int(y_centro - nuevo_alto / 2.0)
        nuevo_y_max = int(y_centro + nuevo_alto / 2.0)

        # Recortar la nube de puntos usando el nuevo bounding box, ignorando la cuarta dimensión
        cropped_arr = point_cloud[nuevo_y_min:nuevo_y_max, nuevo_x_min:nuevo_x_max, :3]

        # Aplanar el arreglo para calcular distancias
        flattened_arr = cropped_arr.reshape(-1, cropped_arr.shape[-1])        

        # Eliminar filas con NaN en las primeras tres columnas
        valid_points = flattened_arr[~np.isnan(flattened_arr).any(axis=1)]

        valid_points = valid_points[np.isfinite(valid_points).all(axis=1)]


        if valid_points.size == 0:
            print("no valid points")
            return None, None

        Q1 = np.percentile(valid_points, 25, axis=0)
        Q3 = np.percentile(valid_points, 75, axis=0)
        IQR = Q3 - Q1
        

        # Calcular los límites para filtrar outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR


        # Filtrar puntos que están dentro de los límites
        conditions = np.all((valid_points >= lower_bound) & (valid_points <= Q1), axis=1)
        filtered_points = valid_points[conditions]
        

        if filtered_points.size == 0:
            print("no valid points after filtering")
            return None, None

        centroide = np.median(filtered_points, axis=0)
        #distancia = np.min(np.linalg.norm(filtered_points, axis=1))
        distancia = np.linalg.norm(centroide)
        
        return distancia, centroide

    def _calculate_angle(self, point):
        """
        Calcula el ángulo utilizando el punto medio del bounding box en el mapa de disparidad.

        :param point_cloud: Nube de puntos en un array numpy.
        :param shape: Forma de la nube de puntos (altura, ancho, canales).
        :param detection: Detección con coordenadas del bounding box.
        :return: Ángulo en grados, y coordenadas x e y del punto medio del bounding box.
        """
        px, py, pz = point
        # Calcular el ángulo en grados
        angle_degrees = np.degrees(np.arctan2(px, pz))
        
        return angle_degrees

    def calculate_steps(self, distance):
        """
        Calcula el número de pasos basado en la distancia y la altura de la persona.

        :param distance: Distancia calculada.
        :return: Número de pasos.
        """
        return distance / self.length_step



    def draw_bboxes(self, image, bboxes, clases):
        """
        Dibuja múltiples bounding boxes en la imagen con el nombre de la clase, la distancia, el ángulo y la confianza.

        Parameters:
        - image: Imagen en la que se dibujarán los bounding boxes.
        - bboxes: Lista de diccionarios con las claves 'class', 'bbox', 'distance', 'angle', y 'conf'.
                Cada 'bbox' es una tupla (x, y, w, h).
        """
        for bbox_info in bboxes:
            x, y, w, h = bbox_info['bbox']
            class_name = clases[int(bbox_info['class'])]
            distance = bbox_info['distance']
            angle = bbox_info['angle']
            conf = bbox_info['conf']
            
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            
            # Dibujar el rectángulo del bbox
            cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 2)
            
            # Preparar los textos
            class_text = f"{class_name} ({conf:.2f})"
            angle_text = f"A: {angle:.2f}"
            distance_text = f"D: {distance:.2f}m"
            
            # Dimensiones del texto
            (class_w, class_h), _ = cv2.getTextSize(class_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            (angle_w, angle_h), _ = cv2.getTextSize(angle_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            (distance_w, distance_h), _ = cv2.getTextSize(distance_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Calcular las posiciones para los textos dentro del bbox
            class_text_position = (x + 5, y + 5 + class_h)  # Arriba dentro del bbox
            angle_text_position = (x + 5, y + 5 + class_h + 5 + angle_h)  # Debajo del texto de la clase
            distance_text_position = (x + 5, y + 5 + class_h + 5 + angle_h + 5 + distance_h)  # Debajo del texto del ángulo
            
            # Fondo para el texto
            cv2.rectangle(image, (x, y), (x + max(class_w, angle_w, distance_w) + 10, y + class_h + angle_h + distance_h + 30), (255, 0, 0), -1)
    
            # Poner los textos en la imagen
            cv2.putText(image, class_text, class_text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(image, angle_text, angle_text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(image, distance_text, distance_text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                


    @staticmethod
    def save_bbox_to_csv(detections, point_cloud_value):
        """
        Guarda los valores del bounding box y la nube de puntos en un archivo CSV.

        :param detections: Lista de detecciones con coordenadas del bounding box.
        :param point_cloud_value: Mapa de disparidad de la imagen.
        """
        for detection in detections:
            x_min, y_min, width, height = map(int, detection['bbox'])
            x_max = x_min + width
            y_max = y_min + height
            cropped_arr = point_cloud_value[y_min:y_max, x_min:x_max]

            # Aplanar el arreglo para crear el DataFrame
            flattened_arr = cropped_arr.reshape(-1, cropped_arr.shape[-1])
            df = pd.DataFrame(flattened_arr, columns=[f'col_{i}' for i in range(flattened_arr.shape[1])])

            # Crear un nombre de archivo único
            csv_filename = f'{detection["class"]}.csv'
            count = 1
            while os.path.exists(csv_filename):
                csv_filename = f'{detection["class"]}_{count}.csv'
                count += 1
            
            # Guardar el DataFrame como CSV
            df.to_csv(csv_filename, index=False)

# Ejemplo de uso:
# if __name__ == "__main__":
#     ubication = Ubication(factor=0.3, person_height=1.75)
    
#     # Supongamos que tienes una lista de detecciones y un mapa de disparidad
#     detections = [
#         {"class": "person", "box": [100, 150, 200, 300]},
#         # Más detecciones...
#     ]
#     point_cloud = np.random.rand(480, 640, 3) * 10  # Mapa de disparidad de ejemplo
#     image = np.zeros((480, 640, 3), dtype=np.uint8)  # Imagen de ejemplo

#     # Calcular y dibujar ubicaciones
#     ubication.calculate_ubication(detections, point_cloud, image)

#     # Guardar bounding boxes y valores de la nube de puntos en CSV
#     #ubication.save_bbox_to_csv(detections, point_cloud)

#     # Mostrar la imagen resultante usando Matplotlib
#     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     plt.title("Ubication")
#     plt.axis('off')  # Desactiva los ejes
#     plt.show()
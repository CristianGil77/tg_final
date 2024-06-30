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
            distance, point, x, y = self.calcular_distancia_mediana(point_cloud, detection['bbox'])
            angle_degrees = self._calculate_angle(point)
            
            detection['distance'] = distance
            detection['angle'] = angle_degrees

            #self.draw_ubication(image, distance, angle_degrees, x, y)

    def calcular_distancia_mediana(self, point_cloud, bbox):
        """
        Calcula la distancia del objeto basada en la mediana del primer y tercer cuartil
        de las distancias en la nube de puntos recortada por el bbox.

        :param point_cloud: Nube de puntos (numpy array) de dimensiones 1280x720x4.
        :param bbox: Bounding box (tupla) con coordenadas (x, y, w, h).
        :return: Distancia del objeto calculada a partir de la mediana del primer y tercer cuartil.
        """
        x_min, y_min, width, height = map(int, bbox)
        x_max = x_min + width
        y_max = y_min + height
        x = int(x_min + width / 2)
        y = int(y_min + height / 2)
        
        # Recortar la nube de puntos usando el bbox, ignorando la cuarta dimensión
        cropped_arr = point_cloud[y_min:y_max, x_min:x_max, :3]
        
        # Aplanar el arreglo para calcular distancias
        flattened_arr = cropped_arr.reshape(-1, cropped_arr.shape[-1])

        print(flattened_arr.shape)

        # Eliminar filas con NaN en las primeras tres columnas
        valid_points = flattened_arr[~np.isnan(flattened_arr).any(axis=1)]
        
        # Calcular las distancias euclidianas ignorando la cuarta dimensión
        distancias = np.sqrt(np.sum(valid_points**2, axis=1))
        
        # Calcular el percentil 25 y 75
        q1 = np.percentile(distancias, 1)

        distancias_filtradas = distancias[(distancias > q1)]

        min_index = np.argmin(distancias_filtradas)
        distancia_minima = distancias_filtradas[min_index]
        punto_minimo = valid_points[min_index]
        
        return distancia_minima, punto_minimo, x, y

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

    def draw_ubication(self, image, distance, angle_degrees, x, y):
        """
        Dibuja la distancia y el ángulo en la imagen en las coordenadas especificadas.

        :param image: Imagen en la que se dibujarán los resultados.
        :param distance: Distancia calculada al objeto.
        :param angle_degrees: Ángulo calculado en grados.
        :param x: Coordenada x en la imagen.
        :param y: Coordenada y en la imagen.
        """
        cv2.putText(image, f"Distance: {distance:.2f}m", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
        cv2.putText(image, f"Angle: {angle_degrees:.2f}", (x, y - 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

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
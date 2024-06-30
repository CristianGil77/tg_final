import numpy as np
import matplotlib.pyplot as plt
import cv2

class Preprocessing:
    def __init__(self, blur_threshold=100.0, clahe_clip_limit=2.0, clahe_tile_grid_size=(8, 8), yaw_angle_min=-60, yaw_angle_max=60):
        """
        Inicializa la clase de preprocesamiento con los parámetros especificados.

        :param blur_threshold: Umbral para la detección de desenfoque.
        :param clahe_clip_limit: Límite de contraste para CLAHE.
        :param clahe_tile_grid_size: Tamaño de la rejilla para CLAHE.
        :param yaw_angle_min: Ángulo mínimo de descarte para yaw (en grados).
        :param yaw_angle_max: Ángulo máximo de descarte para yaw (en grados).
        """
        self.blur_threshold = blur_threshold
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_tile_grid_size = clahe_tile_grid_size
        self.yaw_angle_min = yaw_angle_min
        self.yaw_angle_max = yaw_angle_max

    def discard_frame_based_on_angle(self, angles):
        """nbnbnbnbnbnbnbn
        Descarta fotogramas basados en el ángulo de rotación en el eje Y (yaw).

        :param angles: Lista de ángulos de rotación.
        :return: True si el fotograma debe ser descartado, False en caso contrario.
        """
        yaw_angle = angles[1]
        return self.yaw_angle_min < yaw_angle < self.yaw_angle_max

    def detect_blur(self, image):
        """
        Detecta si una imagen está desenfocada basándose en la varianza del Laplaciano.

        :param image: Imagen en formato RGB.
        :return: True si la imagen está desenfocada, False en caso contrario.
        """
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        return variance < self.blur_threshold

    def equalize_histogram(self, image):
        """
        Equaliza el histograma de una imagen en el espacio de color HSV.

        :param image: Imagen en formato RGB.
        :return: Imagen con el histograma equalizado en formato RGB.
        """
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv_image[:, :, 2] = cv2.equalizeHist(hsv_image[:, :, 2])
        equalized_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
        return equalized_image

    def apply_clahe(self, image):
        """
        Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) a la imagen.

        :param image: Imagen en formato RGB.
        :return: Imagen con CLAHE aplicado en formato RGB.
        """
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        clahe = cv2.createCLAHE(clipLimit=self.clahe_clip_limit, tileGridSize=self.clahe_tile_grid_size)
        hsv_image[:, :, 2] = clahe.apply(hsv_image[:, :, 2])
        clahe_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
        return clahe_image

    def sharpen_image(self, image):
        """
        Aplica un filtro de enfoque a la imagen.

        :param image: Imagen en formato RGB.
        :return: Imagen enfocada en formato RGB.
        """
        kernel = np.array([[0, -1, 0], 
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened_image = cv2.filter2D(image, -1, kernel)
        return sharpened_image


if __name__ == "__main__":
    preprocessing = Preprocessing(
        blur_threshold=100.0, 
        clahe_clip_limit=2.0, 
        clahe_tile_grid_size=(8, 8),
        yaw_angle_min=-60,
        yaw_angle_max=60
    )
    
    # Cargar una imagen de ejemplo en formato RGB
    image = cv2.imread('test/example1.png')

    plt.figure()
    plt.title('Image')
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    # Descartar fotograma basado en ángulo
    angles = [0, 45, 0]  # Ejemplo de ángulos (pitch, yaw, roll)
    discard = preprocessing.discard_frame_based_on_angle(angles)
    print(f"Discard frame: {discard}")

    # Detectar desenfoque
    is_blurry = preprocessing.detect_blur(image)
    print(f"Is image blurry: {is_blurry}")

    # Equalizar histograma
    equalized_image = preprocessing.equalize_histogram(image)
    plt.figure()
    plt.title('Equalized Image')
    plt.imshow(cv2.cvtColor(equalized_image, cv2.COLOR_RGB2BGR))

    # Aplicar CLAHE
    clahe_image = preprocessing.apply_clahe(image)
    plt.figure()
    plt.title('CLAHE Image')
    plt.imshow(cv2.cvtColor(clahe_image, cv2.COLOR_RGB2BGR))

    # Enfocar imagen
    sharpened_image = preprocessing.sharpen_image(image)
    plt.figure()
    plt.title('Sharpened Image')
    plt.imshow(cv2.cvtColor(sharpened_image, cv2.COLOR_RGB2BGR))

    plt.show()

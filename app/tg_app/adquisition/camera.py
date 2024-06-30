import sys
import numpy as np
import pyzed.sl as sl
import cv2
import math
import pycuda.driver as cuda
import pycuda.autoinit


class ZEDCamera:
    def __init__(self, resolution=sl.RESOLUTION.HD720, depth_mode=sl.DEPTH_MODE.ULTRA, sensing_mode=sl.SENSING_MODE.FILL, max_distance=10, min_distance=0.5):
        """
        Inicializa la cámara ZED con los parámetros especificados.

        :param resolution: Resolución de la cámara (HD720, HD1080, etc.).
        :param depth_mode: Modo de profundidad (ULTRA, PERFORMANCE, NEURAL).
        :param sensing_mode: Modo de detección (FILL, STANDARD).
        :param max_distance: Distancia máxima de profundidad en metros.
        :param min_distance: Distancia mínima de profundidad en metros.
        """
        self.zed = sl.Camera()

        # Configuración de parámetros de inicialización
        input_type = sl.InputType()
        if len(sys.argv) >= 2:
            input_type.set_from_svo_file(sys.argv[1])

        init_params = sl.InitParameters(input_t=input_type)
        init_params.camera_resolution = resolution
        init_params.depth_mode = depth_mode
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_maximum_distance = max_distance
        init_params.depth_minimum_distance = min_distance
        #1init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

        # Configuración optimizada para Jetson
        init_params.camera_fps = 30
        # init_params.gpu_id = 0  # Jetson Nano usualmente tiene un solo GPU
        # init_params.sdk_verbose = True  # Para obtener más detalles de la inicialización

        # Abrir la cámara
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            self.zed.close()
            sys.exit(1)

        # Configuración de parámetros de runtime
        self.runtime_params = sl.RuntimeParameters()
        self.runtime_params.sensing_mode = sensing_mode
        self.runtime_params.confidence_threshold = 25
        #self.runtime_params.texture_confidence_threshold = 75

        self.image_size = self.zed.get_camera_information().camera_resolution
        self.image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.depth_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.point_cloud_zed = sl.Mat()
        self.sensors_data = sl.SensorsData()

    def capture_image(self):
        """
        Captura una imagen desde la cámara ZED.

        :return: Imagen capturada en formato OpenCV.
        """
        self.zed.retrieve_image(self.image_zed, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
        image_ocv = self.image_zed.get_data()
        return image_ocv

    def capture_depth_image(self):
        """
        Captura una imagen de profundidad desde la cámara ZED.

        :return: Imagen de profundidad en formato OpenCV.
        """
        self.zed.retrieve_measure(self.depth_zed, sl.MEASURE.DEPTH, sl.MEM.CPU, self.image_size)
        depth_image_ocv = self.depth_zed.get_data()
        return depth_image_ocv
    
    def capture_point_cloud(self):
        """
        Captura la nube de puntos desde la cámara ZED.

        :return: Nube de puntos capturada.
        """
        self.zed.retrieve_measure(self.point_cloud_zed, sl.MEASURE.XYZRGBA, sl.MEM.CPU, self.image_size)
        point_cloud = self.point_cloud_zed.get_data()
        # point_cloud_gpu = cuda.mem_alloc(point_cloud.nbytes)
        # cuda.memcpy_htod(point_cloud_gpu, point_cloud)
        # return point_cloud_gpu, point_cloud.shape

        return point_cloud

    def get_imu_angles(self):
        """
        Obtiene los ángulos de rotación del IMU.

        :return: Lista de ángulos de rotación en grados.
        """
        if self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.IMAGE) == sl.ERROR_CODE.SUCCESS:
            rotation = self.sensors_data.get_imu_data().get_pose().get_euler_angles()
            angles_degrees = [math.degrees(angle) for angle in rotation]
            return angles_degrees
        return None


"""
# Ejemplo de uso:
if __name__ == "__main__":
    zed_camera = ZEDCamera()
    image = zed_camera.capture_image()
    depth_image = zed_camera.capture_depth_image()
    point_cloud = zed_camera.capture_point_cloud()
    imu_angles = zed_camera.get_imu_angles()

    print("IMU Angles:", imu_angles)
    cv2.imshow("ZED Image", image)
    cv2.imshow("Depth Image", depth_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""
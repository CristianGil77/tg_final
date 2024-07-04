from pydub import AudioSegment
from pydub.generators import Sine
from pydub.playback import play
import pyttsx3
import os
import time

class DirectionalAudioGenerator:
    def __init__(self, clases, max_distance=3, feedback_mode=1, audio_speed = 1.0, angle = 30):
        """
        Inicializa la clase DirectionalAudioGenerator con la distancia máxima y la configuración inicial.
        
        :param max_distance: Distancia máxima para generar el audio direccional.
        :param feedback_mode: Modo de retroalimentación de audio (1, 2, 3 o 4).
        """
        self.engine = pyttsx3.init()
        self.max_distance = max_distance
        self.folder_name = "app/tg_app/audio/audios"
        self.mode = feedback_mode
        self.clases = clases
        self.final_audio = None
        self.speed = audio_speed
        self.angle = angle

        self.engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-MX_SABINA_11.0")

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def generate_word_audio(self, word):
        """
        Genera un archivo de audio a partir de una palabra utilizando pyttsx3.
        
        :param word: Palabra para convertir a audio.
        """
        try:
            # Configura la voz y la velocidad de habla
            self.engine.setProperty('rate', 200)  # Velocidad de habla
            self.engine.setProperty('volume', 1)  # Volumen de la voz

            # Guarda el audio generado en un archivo temporal
            audio_name = os.path.join(self.folder_name, f"{word.replace(' ', '_')}.wav")
            
            self.engine.save_to_file(word, audio_name)
            self.engine.runAndWait()  # Espera a que se complete la generación del audio

            # Espera hasta que el archivo exista
            timeout = 100  # Tiempo máximo de espera en segundos
            start_time = time.time()
            while not os.path.exists(audio_name):
                if time.time() - start_time > timeout:
                    raise FileNotFoundError(f"El archivo de audio {audio_name} no se generó dentro del tiempo esperado.")
                time.sleep(0.1)

            print("Audio creado")

        except Exception as e:
            print(f"Error al generar el audio: {e}")
    
    def load_word_audio(self, word):
        """
        Carga un archivo de audio correspondiente a una palabra. Si el archivo no existe, lo genera.
        
        :param word: Palabra para la cual se debe cargar o generar el audio.
        :return: Segmento de audio cargado.
        """
        audio_file = os.path.join(self.folder_name, f"{word.replace(' ', '_')}.wav")

        if os.path.exists(audio_file):
            # Si el archivo existe, carga el audio desde el archivo
            word_audio = AudioSegment.from_wav(audio_file)
        else:
            # Si el archivo no existe, genera el audio y luego lo carga
           
            self.generate_word_audio(word)
            word_audio = AudioSegment.from_wav(audio_file)
        
        return word_audio
    
    def generate_beep_audio(self, duration, frequency=1000, volume=1):
        """
        Genera un tono de bip con una frecuencia y duración específicas.
        
        :param duration: Duración del bip en segundos.
        :param frequency: Frecuencia del bip en Hz.
        :param volume: Volumen del bip.
        :return: Segmento de audio del bip.
        """
        beep_wave = Sine(frequency).to_audio_segment(duration=duration*1000).apply_gain(volume)
        return beep_wave
    
    def load_orientation_audio(self, angle):
        """
        Carga el audio correspondiente a la orientación basada en el ángulo.
        
        :param angle: Ángulo de orientación.
        :return: Segmento de audio de la orientación.
        """
        word = "diagonal derecha" if angle > self.angle else "diagonal izquierda" if angle < -self.angle else "al frente"
        return self.load_word_audio(word)
    
    def load_distance_audio(self, distance):
        """
        Carga el audio correspondiente a la distancia basada en la distancia.
        
        :param distance: Distancia medida.
        :return: Segmento de audio de la distancia.
        """
        word = "un paso" if distance <= 1 else "dos pasos" if distance <= 2 else "tres pasos"
        return self.load_word_audio(word)
    
    def play_audio(self):
        
        #audio = self.final_audio.speedup(playback_speed=self.speed)

        new_frame_rate = int(self.final_audio.frame_rate * self.speed)
        audio = self.final_audio._spawn(self.final_audio.raw_data, overrides={'frame_rate': new_frame_rate})
        play(audio)

    
    def generate_final_audio(self, detection):
        """
        Genera el audio final combinando diferentes elementos según el modo seleccionado.
        
        :param detection: Diccionario que contiene 'class', 'distance' y 'angle' de la detección.
        """
        audio_object = self.load_word_audio(self.clases[int(detection['class'])])

        if self.mode == 1:
            # OBJETO + ORIENTACIÓN + DISTANCIA
            
            self.final_audio = (audio_object + self.load_orientation_audio(detection['angle']) + 
                           self.load_distance_audio(detection['distance']))
            

        elif self.mode == 2:
            # OBJETO + DISTANCIA + BEEP EN 2D
            
            beep_audio = self.generate_beep_audio(0.1)  # Duración del bip: 0.1 segundos
            self.final_audio = audio_object + self.load_distance_audio(detection['distance']) + beep_audio   
            angulo = 70 if detection['angle'] > self.angle else -70 if detection['angle'] < -self.angle else 0
            pan = angulo / 90  # Mapea el ángulo al valor de pan (0 para la izquierda, 1 para la derecha)
            self.final_audio = self.final_audio.pan(pan)
           
        elif self.mode == 3:
            # OBJETO + BEEP CON VOLUMEN BASADO EN DISTANCIA EN 2D
            
            volume = 1 + (self.max_distance - detection['distance'])
            beep_audio = self.generate_beep_audio(0.1, volume=volume**2)
            angulo = 70 if detection['angle'] > self.angle else -70 if detection['angle'] < -self.angle else 0
            pan = angulo / 90  # Mapea el ángulo al valor de pan (0 para la izquierda, 1 para la derecha)
            self.final_audio = (audio_object + beep_audio).pan(pan)
           
        
        elif self.mode == 4:
            # OBJETO + SECUENCIA DE BEEPS EN 2D
            
            beep_sequence = []
            n_beeps = round(detection['distance']) 
            if n_beeps == 0:
                n_beeps = 1

            for _ in range(int(n_beeps)):
                # Genera el bip como un segmento de audio
                beep_audio = self.generate_beep_audio(0.1 * detection['distance'])
                beep_sequence.append(beep_audio)

                if _ < n_beeps - 1:
                    silence_wave = AudioSegment.silent(duration=50)
                    beep_sequence.append(silence_wave)

            # Concatena todos los bips en la secuencia
            sequence_audio = sum(beep_sequence)
            angulo = 75 if detection['angle'] > self.angle else -75 if detection['angle'] < -self.angle else 0
            pan = angulo / 90  # Mapea el ángulo al valor de pan (0 para la izquierda, 1 para la derecha)
            self.final_audio = (audio_object + sequence_audio).pan(pan)
            

        # Exporta el audio final
        
        # final_audio.export(os.path.join(self.folder_name, "directional_audio.wav"), format="wav")
        # print("sonido")
        # play(final_audio)

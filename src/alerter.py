import pygame
import os
import wave
import math
import struct

class Alerter:
    def __init__(self, alarm_file):
        self.alarm_file = alarm_file
        self.playing = False
        
        pygame.mixer.init()
        
        # Determine if we need to generate a sound
        if not os.path.exists(self.alarm_file):
            self._generate_beep(self.alarm_file)
            
        self.sound = pygame.mixer.Sound(self.alarm_file)

    def _generate_beep(self, filename, duration=1.0, freq=440.0):
        # Generate a 440Hz sine wave beep
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        amplitude = 16000 # Max 32767
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            for i in range(n_samples):
                value = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
                data = struct.pack('<h', value)
                wav_file.writeframesraw(data)

    def alert(self):
        if not pygame.mixer.get_busy():
            self.sound.play(-1) # Loop indefinitely
            self.playing = True

    def stop(self):
        if self.playing:
            self.sound.stop()
            self.playing = False

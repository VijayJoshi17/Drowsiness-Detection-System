import time
from collections import deque
from config import EAR_THRESHOLD, EAR_FRAMES, MAR_THRESHOLD, MAR_FRAMES

class Assessor:
    def __init__(self):
        self.ear_counter = 0
        self.mar_counter = 0
        self.drowsy = False
        self.yawning = False
        
        # Blink Rate Logic
        self.last_ear_state = "OPEN" # OPEN or CLOSED
        self.blinks = deque() # Timestamps of blinks
        self.bpm = 0

    def update(self, ear, mar):
        if ear is None or mar is None:
            return

        current_time = time.time()

        # Check Drowsiness (Eyes Closed) and Blink Detection
        if ear < EAR_THRESHOLD:
            self.ear_counter += 1
            current_ear_state = "CLOSED"
        else:
            self.ear_counter = 0
            self.drowsy = False
            current_ear_state = "OPEN"

            # Blink Detection (Transition from OPEN to CLOSED)
        # Add debounce: Only count blink if last blink was > 0.3 seconds ago
        if self.last_ear_state == "OPEN" and current_ear_state == "CLOSED":
            if not self.blinks or (current_time - self.blinks[-1] > 0.3):
                self.blinks.append(current_time)
            
        self.last_ear_state = current_ear_state

        # Clean old blinks (> 60 seconds ago)
        while self.blinks and (current_time - self.blinks[0] > 60):
            self.blinks.popleft()
            
        self.bpm = len(self.blinks)

        if self.ear_counter >= EAR_FRAMES:
            self.drowsy = True

        # Check Yawning (Mouth Open)
        if mar > MAR_THRESHOLD:
            self.mar_counter += 1
        else:
            self.mar_counter = 0
            self.yawning = False

        if self.mar_counter >= MAR_FRAMES:
            self.yawning = True

    def is_drowsy(self):
        return self.drowsy

    def is_yawning(self):
        return self.yawning
        
    def get_bpm(self):
        return self.bpm

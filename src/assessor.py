from config import EAR_THRESHOLD, EAR_FRAMES, MAR_THRESHOLD, MAR_FRAMES

class Assessor:
    def __init__(self):
        self.ear_counter = 0
        self.mar_counter = 0
        self.drowsy = False
        self.yawning = False

    def update(self, ear, mar):
        if ear is None or mar is None:
            return

        # Check Drowsiness (Eyes Closed)
        if ear < EAR_THRESHOLD:
            self.ear_counter += 1
        else:
            self.ear_counter = 0
            self.drowsy = False

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

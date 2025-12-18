import cv2
import mediapipe as mp
import numpy as np
import scipy.spatial.distance as dist

class Detector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True)
        
        # Landmark indices
        # Left eye indices
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        # Right eye indices
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        # Mouth indices (Inner)
        self.MOUTH = [61, 37, 267, 314, 17, 84, 181, 321] # Simplified MAR points: [left, top_left, top_right, right, bottom_right, bottom_left, bottom, top]? 
        # Actually, let's use:
        # 61: Left corner, 291: Right corner
        # 13: Upper lip, 14: Lower lip
        # And some intermediates for MAR calculation
        
        # Re-defining MAR indices for better vertical/horizontal ratio
        # Vertical: (13, 14), (37, 84), (267, 314)
        # Horizontal: (61, 291)
        self.MAR_POINTS = [
            [13, 14], # Top/Bottom Center
            [37, 84], # Left portion
            [267, 314], # Right portion
            [61, 291] # Left Corner / Right Corner (Horizontal)
        ]

    def get_landmarks(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0] # Use first face
        return None

    def calculate_ear(self, landmarks, indices, w, h):
        # EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        # indices: [p1, p2, p3, p4, p5, p6]
        # p1=0, p4=3 (horizontal)
        
        pts = np.array([(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in indices])
        
        # Vertical distances
        A = dist.euclidean(pts[1], pts[5])
        B = dist.euclidean(pts[2], pts[4])
        
        # Horizontal distance
        C = dist.euclidean(pts[0], pts[3])
        
        ear = (A + B) / (2.0 * C)
        return ear

    def calculate_mar(self, landmarks, w, h):
        # A = dist(13, 14)
        # B = dist(37, 84)
        # C = dist(267, 314)
        # D = dist(61, 291)
        # MAR = (A + B + C) / (3 * D) -- average vertical / horizontal
        
        # Points from self.MAR_POINTS
        p_13 = (landmarks.landmark[13].x * w, landmarks.landmark[13].y * h)
        p_14 = (landmarks.landmark[14].x * w, landmarks.landmark[14].y * h)
        p_37 = (landmarks.landmark[37].x * w, landmarks.landmark[37].y * h)
        p_84 = (landmarks.landmark[84].x * w, landmarks.landmark[84].y * h)
        p_267 = (landmarks.landmark[267].x * w, landmarks.landmark[267].y * h)
        p_314 = (landmarks.landmark[314].x * w, landmarks.landmark[314].y * h)
        p_61 = (landmarks.landmark[61].x * w, landmarks.landmark[61].y * h)
        p_291 = (landmarks.landmark[291].x * w, landmarks.landmark[291].y * h)
        
        A = dist.euclidean(p_13, p_14)
        B = dist.euclidean(p_37, p_84)
        C = dist.euclidean(p_267, p_314)
        D = dist.euclidean(p_61, p_291)
        
        mar = (A + B + C) / (3.0 * D)
        return mar

    def process_frame(self, frame):
        h, w = frame.shape[:2]
        landmarks = self.get_landmarks(frame)
        
        if landmarks:
            left_ear = self.calculate_ear(landmarks, self.LEFT_EYE, w, h)
            right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2.0
            
            mar = self.calculate_mar(landmarks, w, h)
            
            return avg_ear, mar, landmarks
        
        return None, None, None

import json
import os
import numpy as np

PROFILE_FILE = "user_profile.json"

class IdentityManager:
    def __init__(self):
        self.profile = self.load_profile()
        self.threshold = 0.02 # MSE Threshold (Tightened to avoid false positives)

    def load_profile(self):
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_profile(self, landmarks):
        """
        Saves the normalized landmarks as the user profile.
        Expects landmarks to be a list of dicts or objects with x, y, z.
        """
        normalized_points = self._normalize_landmarks(landmarks)
        with open(PROFILE_FILE, "w") as f:
            json.dump(normalized_points, f)
        self.profile = normalized_points
        return True

    def verify_user(self, landmarks):
        """
        Compares current landmarks with profile.
        Returns (is_match, score)
        """
        if self.profile is None:
            return False, 0.0
        
        current_points = self._normalize_landmarks(landmarks)
        profile_points = self.profile
        
        # Calculate Mean Squared Error
        mse = np.mean(np.square(np.array(current_points) - np.array(profile_points)))
        
        # Score: 0 is perfect match. 
        # Convert to a confidence-like score? 
        # Let's return raw MSE for debugging and a boolean.
        is_match = bool(mse < self.threshold)
        return is_match, float(mse)

    def _normalize_landmarks(self, landmarks):
        """
        Normalize landmarks to be invariant to scale and translation.
        1. Center around the nose tip (Index 1).
        2. Scale by the bounding box width or inter-ocular distance.
        """
        points = []
        if hasattr(landmarks, "landmark"):
            source = landmarks.landmark
        else:
            source = landmarks

        # Extract points
        coords = np.array([(p.x, p.y, p.z) for p in source])
        
        # 1. Translation: Center at Nose Tip (Index 1)
        # Note: MediaPipe FaceMesh Index 1 is nose tip
        nose_tip = coords[1]
        centered = coords - nose_tip
        
        # 2. Scaling: Normalize by distance between eyes (Index 33 and 263 are outer corners of eyes approx)
        # Or just max absolute value to fit in -1 to 1 range
        # Using max extent is safer for general shape
        max_dist = np.max(np.abs(centered))
        if max_dist > 0:
            normalized = centered / max_dist
        else:
            normalized = centered
            
        return normalized.tolist()

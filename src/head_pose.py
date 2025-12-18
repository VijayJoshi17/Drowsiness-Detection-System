import cv2
import numpy as np

class HeadPoseEstimator:
    def __init__(self, frame_width, frame_height):
        self.w = frame_width
        self.h = frame_height
        
        # 3D model points (Generic human face)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right Mouth corner
        ])

        # Camera internals
        self.focal_length = self.w
        self.center = (self.w / 2, self.h / 2)
        self.camera_matrix = np.array(
            [[self.focal_length, 0, self.center[0]],
             [0, self.focal_length, self.center[1]],
             [0, 0, 1]], dtype="double"
        )
        self.dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion

    def get_pose(self, landmarks):
        # 2D image points from MediaPipe landmarks
        # Indices: Nose tip (1), Chin (152), Left Eye Left (33), Right Eye Right (263), Left Mouth (61), Right Mouth (291)
        # Note: MP uses 263 for right eye outer corner, 33 for left eye outer corner.
        
        # Mapping MP landmarks to Model points
        image_points = np.array([
            (landmarks.landmark[1].x * self.w, landmarks.landmark[1].y * self.h),     # Nose tip
            (landmarks.landmark[152].x * self.w, landmarks.landmark[152].y * self.h), # Chin
            (landmarks.landmark[33].x * self.w, landmarks.landmark[33].y * self.h),   # Left eye left corner
            (landmarks.landmark[263].x * self.w, landmarks.landmark[263].y * self.h), # Right eye right corner
            (landmarks.landmark[61].x * self.w, landmarks.landmark[61].y * self.h),   # Left Mouth corner
            (landmarks.landmark[291].x * self.w, landmarks.landmark[291].y * self.h)  # Right Mouth corner
        ], dtype="double")

        (success, rotation_vector, translation_vector) = cv2.solvePnP(
            self.model_points, 
            image_points, 
            self.camera_matrix, 
            self.dist_coeffs, 
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        return rotation_vector, translation_vector

    def get_euler_angles(self, rotation_vector):
        # Calculate Euler angles
        rmat, jac = cv2.Rodrigues(rotation_vector)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        # Pitch: x, Yaw: y, Roll: z
        return angles[0], angles[1], angles[2]

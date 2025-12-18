import cv2
from config import COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_WHITE

def draw_info(frame, ear, mar, is_drowsy, is_yawning):
    # Draw EAR and MAR values
    cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)
    cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)
    
    # Draw Status
    if is_drowsy:
        cv2.putText(frame, "DROWSINESS ALERT!", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_RED, 2)
    if is_yawning:
        cv2.putText(frame, "YAWNING ALERT!", (10, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_YELLOW, 2)

def draw_landmarks(frame, landmarks, w, h, detector_class):
    # Optional: Draw eye and mouth landmarks for visual feedback
    # We need the indices from the detector class to draw them specifically
    
    for idx in detector_class.LEFT_EYE + detector_class.RIGHT_EYE:
        x = int(landmarks.landmark[idx].x * w)
        y = int(landmarks.landmark[idx].y * h)
        cv2.circle(frame, (x, y), 1, COLOR_GREEN, -1)
        
    for pair in detector_class.MAR_POINTS:
        for idx in pair:
            x = int(landmarks.landmark[idx].x * w)
            y = int(landmarks.landmark[idx].y * h)
            cv2.circle(frame, (x, y), 1, COLOR_YELLOW, -1)

import cv2

# Camera
CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Detection Thresholds
EAR_THRESHOLD = 0.20  # Eye Aspect Ratio threshold (below this is closed)
EAR_FRAMES = 50       # Number of consecutive frames to trigger alert (approx 2 seconds @ 25-30 FPS)
MAR_THRESHOLD = 0.5   # Mouth Aspect Ratio threshold (above this is yawning)
MAR_FRAMES = 50       # Number of consecutive frames to trigger alert

# Colors (B, G, R)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)

# Alert
ALARM_FILE = "alarm.wav"  # You will need to provide this file or I can generate a beep

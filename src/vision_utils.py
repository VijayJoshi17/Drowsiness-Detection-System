import cv2
import numpy as np

def enhance_low_light(frame, brightness_threshold=70, gamma=2.5):
    """
    Checks if the frame is too dark and applies gamma correction if needed.
    Returns: (enhanced_frame, is_low_light)
    """
    # Convert to HSV to check brightness (Value channel)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    avg_brightness = np.mean(v_channel)
    
    is_low_light = avg_brightness < brightness_threshold
    
    if is_low_light:
        # Gamma Correction: Power Law Transform
        # Output = (Input/255) ^ (1/gamma) * 255
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")
        
        enhanced_frame = cv2.LUT(frame, table)
        return enhanced_frame, True
    
    return frame, False

import cv2
import time
from config import CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT, ALARM_FILE
from src.camera import Camera
from src.detector import Detector
from src.assessor import Assessor
from src.alerter import Alerter
import src.ui as ui

def main():
    # Initialize components
    cam = Camera(src=CAMERA_ID, width=FRAME_WIDTH, height=FRAME_HEIGHT).start()
    detector = Detector()
    assessor = Assessor()
    alerter = Alerter(ALARM_FILE)
    
    print("System Started. Press 'q' to quit.")
    
    prev_time = 0
    
    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue
            
            # FPS Calculation
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            
            # Processing
            ear, mar, landmarks = detector.process_frame(frame)
            
            if landmarks:
                assessor.update(ear, mar)
                
                is_drowsy = assessor.is_drowsy()
                is_yawning = assessor.is_yawning()
                
                # Alert Logic
                if is_drowsy:
                    alerter.alert()
                else:
                    alerter.stop() # Stop if not drowsy? Or should Yawning also trigger?
                    # Yawning is usually a warning, not an immediate danger like closing eyes.
                    # But prompt says "Alert & Warning System... Activate audible alarms".
                    # I'll implement logic: Drowsy = Continuous Alarm. Yawning = Maybe just visual or short beep.
                    # For now, let's make Drowsy the main trigger for the alarm.
                
                # Drawing
                h, w = frame.shape[:2]
                ui.draw_landmarks(frame, landmarks, w, h, detector)
                ui.draw_info(frame, ear, mar, is_drowsy, is_yawning)
                
            cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Driver Drowsiness Detection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        cam.stop()
        alerter.stop()
        cv2.destroyAllWindows()
        print("System Stopped.")

if __name__ == "__main__":
    main()

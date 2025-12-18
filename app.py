from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import time
import json
import threading
from config import CAMERA_ID, FRAME_WIDTH, FRAME_HEIGHT, ALARM_FILE
from src.camera import Camera
from src.detector import Detector
from src.assessor import Assessor
from src.alerter import Alerter
from src.head_pose import HeadPoseEstimator
from src.analytics import SessionManager
import src.ui as ui

app = Flask(__name__)

# Global Components
camera = None
detector = None
assessor = None
alerter = None
head_pose = None
session_manager = None

# Global State for API
current_status = {
    "ear": 0,
    "mar": 0,
    "pitch": 0,
    "yaw": 0,
    "drowsy": False,
    "yawning": False,
    "distracted": False,
    "fps": 0
}
lock = threading.Lock()

def init_system():
    global camera, detector, assessor, alerter, head_pose, session_manager
    if camera is None:
        camera = Camera(src=CAMERA_ID, width=FRAME_WIDTH, height=FRAME_HEIGHT).start()
        detector = Detector()
        assessor = Assessor()
        alerter = Alerter(ALARM_FILE)
        head_pose = HeadPoseEstimator(FRAME_WIDTH, FRAME_HEIGHT)
        session_manager = SessionManager()

def gen_frames():
    global current_status, camera, detector, assessor, alerter, head_pose, session_manager
    
    prev_time = 0
    
    while True:
        frame = camera.read()
        if frame is None:
            break
            
        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        # Process
        ear, mar, landmarks = detector.process_frame(frame)
        pitch, yaw, roll = 0, 0, 0
        distracted = False
        
        if landmarks:
            # Drowsiness & Yawn
            assessor.update(ear, mar)
            drowsy = assessor.is_drowsy()
            yawning = assessor.is_yawning()
            
            # Head Pose
            rot_vec, trans_vec = head_pose.get_pose(landmarks)
            pitch, yaw, roll = head_pose.get_euler_angles(rot_vec)

            # Normalization: User reports "Straight" is ~ -177.6.
            # This suggests a 180-degree flip in the coordinate system.
            # We wrap the angle to be within -90 to 90 for intuitive "looking up/down".
            if pitch < -90:
                pitch += 180
            elif pitch > 90:
                pitch -= 180
            
            # Distraction Logic (Relaxed thresholds)
            if abs(pitch) > 30 or abs(yaw) > 50:
                distracted = True
                
            # Update Global State
            with lock:
                current_status = {
                    "ear": float(ear),
                    "mar": float(mar),
                    "pitch": float(pitch),
                    "yaw": float(yaw),
                    "drowsy": drowsy,
                    "yawning": yawning,
                    "distracted": distracted,
                    "bpm": assessor.get_bpm(),
                    "fps": fps
                }
            
            # Analytics
            session_manager.log_data(ear, mar, pitch, yaw)
            if drowsy: session_manager.log_event("DROWSY")
            if yawning: session_manager.log_event("YAWN")
            if distracted: session_manager.log_event("DISTRACTED")
            
            # Alerts
            if drowsy:
                alerter.alert()
                cv2.putText(frame, "DROWSY!", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            elif distracted:
                # alerter.alert() # Optional: alert on distraction too?
                cv2.putText(frame, "DISTRACTED!", (10, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            else:
                alerter.stop()
                
            if yawning:
                cv2.putText(frame, "YAWNING!", (10, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Draw Landmarks
            h, w = frame.shape[:2]
            ui.draw_landmarks(frame, landmarks, w, h, detector)
            
            # Draw Pose Axis (Nose tip)
            # Projected nose tip
            nose_end_point2D, _ = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rot_vec, trans_vec, head_pose.camera_matrix, head_pose.dist_coeffs)
            p1 = (int(landmarks.landmark[1].x * w), int(landmarks.landmark[1].y * h))
            p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
            cv2.line(frame, p1, p2, (255, 0, 0), 2)

        # Encode header
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_session')
def start_session():
    init_system()
    return jsonify({"status": "started"})

@app.route('/video_feed')
def video_feed():
    if camera is None or not camera.started:
        # Return a placeholder or empty response if not started
        # For simplicity, we can just return a 204 No Content or a blank image generator
        # But clients might hang. Let's just ensure it doesn't crash.
        return Response("", mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    # Only return status if running
    if camera and camera.started:
        with lock:
            return jsonify(current_status)
    return jsonify({"error": "stopped"})

@app.route('/stop_session')
def stop_session():
    global camera, alerter, session_manager
    
    # Generate Report
    report = {}
    if session_manager:
        report = session_manager.save_report()
    
    # Stop Components
    if camera: 
        camera.stop()
        camera = None
    if alerter: 
        alerter.stop()
        alerter = None
        
    return jsonify(report)



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False) # use_reloader=False because of threading
    finally:
        if camera: camera.stop()
        if alerter: alerter.stop()

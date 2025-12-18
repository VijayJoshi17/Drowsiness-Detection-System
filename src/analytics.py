import time
import json
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.start_time = time.time()
        self.events = [] # List of {timestamp, type, value}
        self.data_points = [] # List of {timestamp, ear, mar, pitch, yaw}
        self.status = "ACTIVE"
        
    def log_data(self, ear, mar, pitch, yaw):
        self.data_points.append({
            "timestamp": time.time() - self.start_time,
            "ear": float(ear) if ear else 0,
            "mar": float(mar) if mar else 0,
            "pitch": float(pitch) if pitch else 0,
            "yaw": float(yaw) if yaw else 0
        })

    def log_event(self, event_type):
        # Avoid spamming events? (Debounce handled by assessor usually)
        # We'll rely on the caller to only log when state changes or alert triggers
        self.events.append({
            "timestamp": time.time() - self.start_time,
            "type": event_type,
            "real_time": datetime.now().strftime("%H:%M:%S")
        })

    def get_summary(self):
        duration = time.time() - self.start_time
        total_frames = len(self.data_points)
        avg_fps = total_frames / duration if duration > 0 else 30.0
        
        # Calculate roughly how many seconds each event type lasted
        # timestamp difference approach is better but count/fps is a good approximation for continuous streams
        seconds_per_frame = 1.0 / avg_fps if avg_fps > 0 else 0.033
        
        drowsy_count = len([e for e in self.events if e['type'] == 'DROWSY'])
        yawn_count = len([e for e in self.events if e['type'] == 'YAWN'])
        distract_count = len([e for e in self.events if e['type'] == 'DISTRACTED'])
        
        drowsy_time = drowsy_count * seconds_per_frame
        yawn_time = yawn_count * seconds_per_frame
        distracted_time = distract_count * seconds_per_frame

        # Scoring: Lose 10 points per sec of drowsiness, 2 per sec of distraction, 5 per yawn event?
        # Actually yawning is continuousframes too.
        score = 100 - (drowsy_time * 5 + distracted_time * 2 + yawn_time * 2)
        
        return {
            "duration_seconds": int(duration),
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "counts": {
                "drowsy": int(drowsy_count),
                "distracted": int(distract_count),
                "yawn": int(yawn_count)
            },
            "times": {
                "drowsy_str": f"{drowsy_time:.1f}s",
                "distracted_str": f"{distracted_time:.1f}s",
                "yawn_str": f"{yawn_time:.1f}s"
            },
            "score": max(0, int(score)) 
        }

    def save_report(self, filepath="session_report.json"):
        report = {
            "summary": self.get_summary(),
            "events": self.events,
            # "data": self.data_points # Optional: Save full data if needed
        }
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=4)
        return report

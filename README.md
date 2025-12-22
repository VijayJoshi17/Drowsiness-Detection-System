# Driver Guard AI - Advanced Drowsiness Detection System

**Driver Guard AI** is a real-time computer vision system designed to enhance driver safety by detecting signs of drowsiness, fatigue, and distraction. Built with **Flask**, **OpenCV**, and **MediaPipe**, it features a modern web dashboard, biometric authentication, and detailed session analytics.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-orange)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)

## 🌟 Key Features

- **Drowsiness Detection**: Monitors Eye Aspect Ratio (EAR) to detect prolonged eye closure.
- **Yawn Detection**: Tracks Mouth Aspect Ratio (MAR) to identify signs of fatigue.
- **Distraction Detection**: Estimates Head Pose (Pitch, Yaw) to alert when the driver looks away.
- ** Blink Rate Analysis**: Calculates Blinks Per Minute (BPM) as a metric for alertness.
- **Face Recognition Login**: Secure, biometric driver identification using geometric landmark matching (no external heavy dependencies).
- **Real-time Dashboard**: Glassmorphism UI showing live video feed, status indicators, and real-time charts.
- **📈 Session Analytics**: Generates a detailed post-drive report with focus scores, event counts, and time distribution charts.
- **🔊 Audio Alerts**: Plays alarm sounds when dangerous behavior is detected.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, MediaPipe Face Mesh
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Chart.js)
- **Math/Data**: NumPy, SciPy

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/VijayJoshi17/Drowsiness-Detection-System.git
    ```

2.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

1.  **Run the Application**:
    ```bash
    run.bat
    # OR
    python app.py
    ```

2.  **Access the Dashboard**:
    Open your browser and go to `http://127.0.0.1:5000`.

3.  **Start Driving**:
    - Click **"Start Session"**.
    - **Register Face** (Optional): Click "Register Face" to link your biometric profile. Status will change from **LOCKED** to **UNLOCKED**.
    - The system will monitor your eyes, mouth, and head position.
    - If you close your eyes, yawn, or look away, an alert will sound and the UI will flash warnings.

4.  **End Session**:
    - Click **"End Session"** to view your **Driver Report Card**.

## 🐳 Docker Deployment

You can run the application in a container without installing dependencies manually.

1.  **Build the Image**:
    ```bash
    docker build -t driver-guard .
    ```

2.  **Run the Container**:
    ```bash
    # We map port 5000 and pass the device for camera access (Linux/WSL)
    # On Windows, accessing the webcam from Docker can be tricky.
    # Standard run command:
    docker run -p 5000:5000 driver-guard
    ```

    *Note: Webcam access inside Docker on Windows requires special configuration or WSL2 USB passthrough. For local development, running `python app.py` directly is recommended.*

## ⚙️ Configuration

You can tune sensitivity settings in `config.py`:

```python
EAR_THRESHOLD = 0.22  # Lower = Less sensitive to eye closure
EAR_FRAMES = 50       # Frames to wait before alert (approx 2s)
MAR_THRESHOLD = 0.5   # Size of mouth opening for yawn
```

## 📁 Project Structure

```
├── app.py              # Flask Application Entry Point
├── config.py           # Configuration Parameters
├── src/
│   ├── camera.py       # Threaded Camera Capture
│   ├── detector.py     # MediaPipe Landmark Detection
│   ├── assessor.py     # Logic for Drowsiness/Yawn/Blink
│   ├── head_pose.py    # Head Orientation Logic
│   ├── identity.py     # Face Recognition Module
│   ├── analytics.py    # Session Logging & Reporting
│   ├── alerter.py      # Audio Alarms
│   └── ui.py           # Video Overlay Drawing
├── templates/
│   └── index.html      # Dashboard UI
├── static/
│   ├── css/style.css   # Styles
│   └── js/main.js      # Frontend Logic & Charts
├── requirements.txt    # Dependencies
├── run.bat             # Batch file to run the application
├── README.md           # Project Documentation
├── .gitignore          # Git ignore file
└── alarm.wav           # Alarm sound file
```

*Stay Alert, Stay Safe!* 🛡️

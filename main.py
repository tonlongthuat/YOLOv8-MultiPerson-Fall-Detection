import cv2
import numpy as np
import time
from flask import Flask, render_template, Response
from esp32cam_streamer import ESP32CamStreamer
from fall_detector import FallDetector
from pose_estimator import PoseEstimator
from video import VideoProcessor, VideoStreamer

app = Flask(__name__)

# ESP32-CAM URL
ESP32_CAM_URL = "http://192.168.1.8"  # Update this URL if needed

# Initialize components
pose_estimator = PoseEstimator()
fall_detector = FallDetector()
esp32_cam = ESP32CamStreamer(ESP32_CAM_URL)
video_processor = VideoProcessor(pose_estimator, fall_detector)
video_streamer = VideoStreamer(esp32_cam, video_processor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_streamer.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
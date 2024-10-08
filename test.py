import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import os
from threading import Thread
import queue
from pose_estimator import PoseEstimator
from fall_detector import FallDetector
from video import VideoProcessor,VideoStreamer
app = Flask(__name__)

# Global variables
current_video_path = None
frame_queue = queue.Queue(maxsize=10)
processing_thread = None
stop_processing = False

pose_estimator = PoseEstimator()
fall_detector = FallDetector()
video_processor = VideoProcessor(pose_estimator, fall_detector)
video_streamer = VideoStreamer(frame_queue)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_video_path, processing_thread, stop_processing
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        current_video_path = file_path
        
        if processing_thread and processing_thread.is_alive():
            stop_processing = True
            processing_thread.join()
        
        stop_processing = False
        processing_thread = Thread(target=process_video)
        processing_thread.start()
        
        return jsonify({'message': 'File uploaded successfully'}), 200

def process_video():
    global current_video_path, frame_queue, stop_processing

    cap = cv2.VideoCapture(current_video_path)
    
    while cap.isOpened() and not stop_processing:
        success, frame = cap.read()
        if not success:
            break

        processed_frame = video_processor.process_frame(frame)

        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(processed_frame)
        time.sleep(0.03)

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(video_streamer.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
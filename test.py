import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import os
from threading import Thread
import queue
from ultralytics import YOLO

app = Flask(__name__)

class PoseEstimator:
    def __init__(self, model_path='yolov8n-pose.pt'):
        self.model = YOLO(model_path)

    def estimate_pose(self, frame):
        return self.model(frame)

class FallDetector:
    def __init__(self, fall_threshold=45, fall_duration=2.0):
        self.fall_threshold = fall_threshold
        self.fall_duration = fall_duration
        self.person_trackers = {}

    def determine_pose(self, keypoints):
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        
        shoulder_mid = np.mean([left_shoulder, right_shoulder], axis=0)
        hip_mid = np.mean([left_hip, right_hip], axis=0)
        
        torso_vector = shoulder_mid - hip_mid
        vertical_vector = np.array([0, -1])
        
        angle = np.arccos(np.dot(torso_vector, vertical_vector) / 
                          (np.linalg.norm(torso_vector) * np.linalg.norm(vertical_vector)))
        angle_degrees = np.degrees(angle)
        
        return "LYING" if angle_degrees >= self.fall_threshold else "STANDING"

    def detect_fall(self, person_id, pose):
        if person_id not in self.person_trackers:
            self.person_trackers[person_id] = {'lying_start_time': None}

        if pose == "LYING":
            if self.person_trackers[person_id]['lying_start_time'] is None:
                self.person_trackers[person_id]['lying_start_time'] = time.time()
            elif time.time() - self.person_trackers[person_id]['lying_start_time'] >= self.fall_duration:
                return True
        else:
            self.person_trackers[person_id]['lying_start_time'] = None

        return False

class VideoProcessor:
    def __init__(self, pose_estimator, fall_detector):
        self.pose_estimator = pose_estimator
        self.fall_detector = fall_detector

    def process_frame(self, frame):
        results = self.pose_estimator.estimate_pose(frame)
        
        for r in results:
            boxes = r.boxes
            poses = r.keypoints

            for i, (box, pose) in enumerate(zip(boxes, poses)):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                keypoints = pose.xy[0].cpu().numpy()
                
                current_pose = self.fall_detector.determine_pose(keypoints)
                fall_detected = self.fall_detector.detect_fall(i, current_pose)

                self.draw_annotations(frame, x1, y1, x2, y2, keypoints, current_pose, fall_detected)

        return frame

    def draw_annotations(self, frame, x1, y1, x2, y2, keypoints, pose, fall_detected):
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, pose, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        for kp in keypoints:
            cv2.circle(frame, (int(kp[0]), int(kp[1])), 4, (0, 255, 0), -1)

        if fall_detected:
            cv2.putText(frame, "FALL DETECTED", (x1, y1 - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

class VideoStreamer:
    def __init__(self, frame_queue):
        self.frame_queue = frame_queue

    def get_frame(self):
        while True:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                time.sleep(0.1)

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
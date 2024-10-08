import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
import mediapipe as mp
import os
from threading import Thread
import queue

app = Flask(__name__)

# Global variables
current_video_path = None
frame_queue = queue.Queue(maxsize=10)
processing_thread = None
stop_processing = False

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
        
        # Stop existing processing thread if any
        if processing_thread and processing_thread.is_alive():
            stop_processing = True
            processing_thread.join()
        
        # Start new processing thread
        stop_processing = False
        processing_thread = Thread(target=process_video)
        processing_thread.start()
        
        return jsonify({'message': 'File uploaded successfully'}), 200

def determine_pose(landmarks):
    # Extract key points
    shoulder_mid = np.mean([
        [landmarks[11].x, landmarks[11].y, landmarks[11].z],  # Left shoulder
        [landmarks[12].x, landmarks[12].y, landmarks[12].z]   # Right shoulder
    ], axis=0)
    
    hip_mid = np.mean([
        [landmarks[23].x, landmarks[23].y, landmarks[23].z],  # Left hip
        [landmarks[24].x, landmarks[24].y, landmarks[24].z]   # Right hip
    ], axis=0)
    
    # Calculate angle between torso and vertical axis
    torso_vector = shoulder_mid - hip_mid
    vertical_vector = np.array([0, -1, 0])  # Pointing downwards
    
    angle = np.arccos(np.dot(torso_vector, vertical_vector) / 
                      (np.linalg.norm(torso_vector) * np.linalg.norm(vertical_vector)))
    angle_degrees = np.degrees(angle)
    
    # Classify pose
    if angle_degrees < 45:  # You can adjust this threshold
        return "STANDING"
    else:
        return "LYING"

def process_video():
    global current_video_path, frame_queue, stop_processing

    mpPose = mp.solutions.pose
    pose = mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mpDraw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(current_video_path)
    
    person_trackers = {}  # Dictionary to track each person's state

    while cap.isOpened() and not stop_processing:
        success, img = cap.read()
        if not success:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        fall_detected = False

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            current_pose = determine_pose(landmarks)

            # Get nose position for labeling
            nose = landmarks[0]
            h, w, c = img.shape
            nose_x, nose_y = int(nose.x * w), int(nose.y * h)

            # Display pose label above head
            cv2.putText(img, current_pose, (nose_x - 30, nose_y - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Draw pose
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            # Track lying duration
            if 'lying_start_time' not in person_trackers:
                person_trackers['lying_start_time'] = None

            if current_pose == "LYING":
                if person_trackers['lying_start_time'] is None:
                    person_trackers['lying_start_time'] = time.time()
                elif time.time() - person_trackers['lying_start_time'] >= 2.0:
                    fall_detected = True
            else:
                person_trackers['lying_start_time'] = None

        # Display fall detection alert
        if fall_detected:
            cv2.putText(img, "FALL DETECTION", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(img)
        time.sleep(0.03)  # Adjust this value to change playback speed

    cap.release()

def gen():
    while True:
        if not frame_queue.empty():
            img = frame_queue.get()
            _, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
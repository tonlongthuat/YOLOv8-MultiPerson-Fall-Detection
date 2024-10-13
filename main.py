from flask import Flask, render_template, Response, request, jsonify
import os
import queue
from pose_estimator import PoseEstimator
from fall_detector import FallDetector
from video import VideoProcessor, VideoStreamer

app = Flask(__name__, template_folder='templates')

# Global variables
frame_queues = {
    0: queue.Queue(maxsize=10),
    1: queue.Queue(maxsize=10),
    2: queue.Queue(maxsize=10),
    3: queue.Queue(maxsize=10)
}

pose_estimator = PoseEstimator()
fall_detector = FallDetector()

# Initialize VideoProcessors for each camera
video_processors = {
    camera_id: VideoProcessor(pose_estimator, fall_detector, frame_queues[camera_id])
    for camera_id in frame_queues
}

video_streamers = {
    camera_id: VideoStreamer(frame_queues[camera_id])
    for camera_id in frame_queues
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    camera_id = int(request.form.get('camera_id'))  
    if camera_id not in frame_queues:
        return jsonify({'error': 'Invalid camera ID'}), 400

    filename = file.filename
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

  
    video_processors[camera_id].start_processing(file_path, camera_id)

    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    if camera_id not in frame_queues:
        return "Camera ID not found", 404
    return Response(video_streamers[camera_id].get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)

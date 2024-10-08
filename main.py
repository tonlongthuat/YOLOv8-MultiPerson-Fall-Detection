from flask import Flask, render_template, Response, request, jsonify
import os
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
video_processor = VideoProcessor(pose_estimator, fall_detector, frame_queue)
video_streamer = VideoStreamer(frame_queue)

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
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # Start processing the new video
        video_processor.start_processing(file_path)
        
        return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/video_feed')
def video_feed():
    return Response(video_streamer.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
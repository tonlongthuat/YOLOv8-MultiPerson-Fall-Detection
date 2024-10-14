from flask import Flask, render_template, Response, request, jsonify
import os
import queue
from esp32cam_streamer import ESP32CamStreamer
from pose_estimator import PoseEstimator
from fall_detector import FallDetector
from video import VideoProcessor, VideoStreamer, FileVideoStreamer

app = Flask(__name__, template_folder='templates')

# Global variables
frame_queues = {
    0: queue.Queue(maxsize=10),
    1: queue.Queue(maxsize=10),
    2: queue.Queue(maxsize=10),
    3: queue.Queue(maxsize=10)
}
ip_addresses = {}

pose_estimator = PoseEstimator()
fall_detector = FallDetector()

# Initialize VideoProcessors for each camera
video_processors = {
    camera_id: VideoProcessor(pose_estimator, fall_detector, frame_queues[camera_id])
    for camera_id in frame_queues
}

video_streamers = {
    camera_id: FileVideoStreamer(frame_queues[camera_id])
    for camera_id in frame_queues
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_ip', methods=['POST'])
def set_ip():
    # Lấy ip từ index.html ip có dạng {camera_id: 192.168.1.8} ví dụ: {0:192.168.1.8}
    data = request.get_json()
    camera_id = data.get('camera_id')
    ip_address = data.get('ip')
    ip_addresses[camera_id] = ip_address
    return jsonify({'message': 'IP address set successfully'}), 200

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
    if camera_id in ip_addresses:
        ip_address = ip_addresses[camera_id]
        esp32_cam = ESP32CamStreamer(ip_address)
        video_processor = video_processors[camera_id]
        streamer = VideoStreamer(esp32_cam, video_processor)
        return Response(streamer.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif camera_id in frame_queues:
        streamer = video_streamers[camera_id]
        return Response(streamer.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({'error': 'Camera ID not found'}), 404

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)

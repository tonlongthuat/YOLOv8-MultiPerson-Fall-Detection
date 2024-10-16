import cv2
import time
from threading import Thread
from ultralytics import YOLO

class VideoProcessor:
    def __init__(self, model_path, frame_queue, confidence_threshold=0.5):
        self.model = YOLO(model_path)
        self.frame_queue = frame_queue
        self.confidence_threshold = confidence_threshold
        self.should_stop = False
        self.processing_thread = None
        self.total_fall_time = 0
        self.fall_detected_duration = 2  # seconds
        self.monitoring_duration = 10  # seconds
        self.start_time = time.time()
        self.last_detection_time = None

    def process_frame(self, frame):
        results = self.model(frame)
        falling_detected = False

        for result in results:
            for box in result.boxes:
                if box.conf < self.confidence_threshold:
                    continue  # Skip detections with low confidence

                class_id = box.cls
                class_name = self.model.names[int(class_id)]
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Put class label text
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if class_name == 'fall':
                    falling_detected = True
                    if self.last_detection_time is None:
                        self.last_detection_time = time.time()
                    else:
                        self.total_fall_time += time.time() - self.last_detection_time
                        self.last_detection_time = time.time()
                    break

        if not falling_detected:
            self.last_detection_time = None

        # Check if total fall time exceeds the threshold within the monitoring duration
        if self.total_fall_time >= self.fall_detected_duration:
            cv2.putText(frame, "FALL DETECTED", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Reset total fall time and start time if monitoring duration has passed
        if time.time() - self.start_time >= self.monitoring_duration:
            self.total_fall_time = 0
            self.start_time = time.time()

        return frame

    def process_video(self, video_path, camera_id):
        self.should_stop = False
        cap = cv2.VideoCapture(video_path)
        
        while cap.isOpened() and not self.should_stop:
            success, frame = cap.read()
            if not success:
                break

            processed_frame = self.process_frame(frame)

            if self.frame_queue.full():
                self.frame_queue.get()
            self.frame_queue.put(processed_frame)
            time.sleep(0.03)

        cap.release()

    def start_processing(self, video_path, camera_id):
        if self.processing_thread and self.processing_thread.is_alive():
            self.stop_processing()
        self.processing_thread = Thread(target=self.process_video, args=(video_path, camera_id))
        self.processing_thread.start()

    def stop_processing(self):
        self.should_stop = True
        if self.processing_thread:
            self.processing_thread.join()

class VideoStreamer:
    def __init__(self, esp32_cam, video_processor):
        self.esp32_cam = esp32_cam
        self.video_processor = video_processor

    def start(self):
        self.esp32_cam.start()

    def stop(self):
        self.esp32_cam.stop()

    def generate_frames(self):
        self.start()
        try:
            while True:
                frame = self.esp32_cam.get_frame()
                if frame is not None:
                    processed_frame = self.video_processor.process_frame(frame)
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                else:
                    time.sleep(0.01)
        finally:
            self.stop()
            
class FileVideoStreamer:
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

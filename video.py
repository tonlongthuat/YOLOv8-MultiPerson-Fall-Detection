import cv2
import time
import numpy as np
from queue import Queue
from threading import Thread

class VideoProcessor:
    def __init__(self, pose_estimator, fall_detector, frame_queue):
        self.pose_estimator = pose_estimator
        self.fall_detector = fall_detector
        self.frame_queue = frame_queue
        self.should_stop = False
        self.processing_thread = None

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

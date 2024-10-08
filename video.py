import cv2
import time
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
    

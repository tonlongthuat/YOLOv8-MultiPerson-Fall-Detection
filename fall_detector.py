import numpy as np
import time
class FallDetector:
    def __init__(self, fall_threshold=45, fall_duration=2.0):
        # Initialize the fall threshold(góc nghiên so với trục thẳng) and the fall duration
        self.fall_threshold = fall_threshold
        self.fall_duration = fall_duration
        self.person_trackers = {}

    def determine_pose(self, keypoints):
        # Extract the keypoints
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        
        # Calculate the midpoints of the shoulders and hips
        shoulder_mid = np.mean([left_shoulder, right_shoulder], axis=0)
        hip_mid = np.mean([left_hip, right_hip], axis=0)
        
        # Calculate the torso vector(vecto từ giữa hông đến giữa vai) and the vertical vector
        torso_vector = shoulder_mid - hip_mid
        vertical_vector = np.array([0, -1])
        
        # Calculate the angle between the torso vector and the vertical vector in degrees 
        # cos góc = tích vô hướng / tích độ dài
        angle = np.arccos(np.dot(torso_vector, vertical_vector) / 
                          (np.linalg.norm(torso_vector) * np.linalg.norm(vertical_vector)))
        angle_degrees = np.degrees(angle)
        # Return the pose based on the angle
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
import numpy as np
import time

class FallDetector:
    def __init__(self, fall_threshold=45, fall_duration=2.0, sit_threshold=50, chair_height_ratio=0.6):
        self.fall_threshold = fall_threshold
        self.fall_duration = fall_duration
        self.sit_threshold = sit_threshold
        self.chair_height_ratio = chair_height_ratio
        self.person_trackers = {}

    def determine_pose(self, keypoints):
        # Extract keypoints
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        left_knee = keypoints[13]
        right_knee = keypoints[14]
        left_ankle = keypoints[15]
        right_ankle = keypoints[16]
        
        # Calculate midpoints
        shoulder_mid = np.mean([left_shoulder, right_shoulder], axis=0)
        hip_mid = np.mean([left_hip, right_hip], axis=0)
        knee_mid = np.mean([left_knee, right_knee], axis=0)
        ankle_mid = np.mean([left_ankle, right_ankle], axis=0)
        
        # Calculate vectors
        torso_vector = shoulder_mid - hip_mid
        thigh_vector = knee_mid - hip_mid
        lower_leg_vector = ankle_mid - knee_mid
        vertical_vector = np.array([0, -1])
        
        # Calculate angles
        torso_angle = self.calculate_angle(torso_vector, vertical_vector)
        knee_angle = self.calculate_angle(thigh_vector, lower_leg_vector)
        
        # Calculate hip height ratio
        total_height = np.linalg.norm(shoulder_mid - ankle_mid)
        hip_height = np.linalg.norm(hip_mid - ankle_mid)
        hip_height_ratio = hip_height / total_height

        # Determine pose
        if torso_angle >= self.fall_threshold:
            return "LYING"
        elif torso_angle >= self.sit_threshold:
            if hip_height_ratio <= self.chair_height_ratio:
                return "SITTING_CHAIR"
            else:
                return "SITTING_FLOOR"
        else:
            return "STANDING"

    def calculate_angle(self, vector1, vector2):
        angle = np.arccos(np.dot(vector1, vector2) / 
                          (np.linalg.norm(vector1) * np.linalg.norm(vector2)))
        return np.degrees(angle)

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
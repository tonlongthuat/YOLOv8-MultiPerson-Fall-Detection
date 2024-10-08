from ultralytics import YOLO

class PoseEstimator:
    def __init__(self, model_path='yolov8n-pose.pt'):
        self.model = YOLO(model_path)

    def estimate_pose(self, frame):
        return self.model(frame,conf=0.5)
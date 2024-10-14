import cv2
import requests
import numpy as np
from collections import deque
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor, as_completed

class ESP32CamStreamer:
    def __init__(self, esp32_cam_url, buffer_size=5, max_workers=3):
        self.esp32_cam_url = esp32_cam_url
        self.buffer_size = buffer_size
        self.frame_buffer = deque(maxlen=buffer_size)
        self.lock = Lock()
        self.stop_event = Event()
        self.max_workers = max_workers

    def start(self):
        self.stop_event.clear()
        self.capture_thread = Thread(target=self._capture_loop)
        self.capture_thread.start()

    def stop(self):
        self.stop_event.set()
        self.capture_thread.join()

    def _capture_loop(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self.stop_event.is_set():
                futures = [executor.submit(self._fetch_frame) for _ in range(self.max_workers)]
                for future in as_completed(futures):
                    frame = future.result()
                    if frame is not None:
                        with self.lock:
                            self.frame_buffer.append(frame)

    def _fetch_frame(self):
        try:
            response = requests.get(self.esp32_cam_url, timeout=1)
            if response.status_code == 200:
                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return frame
        except requests.exceptions.RequestException:
            pass
        return None

    def get_frame(self):
        with self.lock:
            return self.frame_buffer[-1] if self.frame_buffer else None
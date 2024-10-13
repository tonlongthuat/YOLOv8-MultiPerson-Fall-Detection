import cv2
import requests
import numpy as np
from collections import deque
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor, as_completed

class ESP32CamStreamer:
    def __init__(self, esp32_cam_url, buffer_size=5, max_workers=3):
        self.esp32_cam_url = esp32_cam_url
        self.buffer_size = buffer_size #max number of frames to store in the buffer
        self.frame_buffer = deque(maxlen=buffer_size) #buffer to store frames, deque is used to limit the size of the buffer
        self.lock = Lock() #Ensures that while one thread is adding a frame to the buffer, another isn't trying to read from it
        self.stop_event = Event() #Allows for the stopping of the frame capture loop
        self.max_workers = max_workers #The number of threads used to fetch frames

    def start(self):
        #start the capture loop
        self.stop_event.clear()
        self.capture_thread = Thread(target=self._capture_loop)
        self.capture_thread.start()

    def stop(self):
        #stop the capture loop
        self.stop_event.set()
        self.capture_thread.join()

    def _capture_loop(self):
        #fetch frames from the ESP32-CAM
        #sử dụng ThreadPoolExecutor để lấy nhiều frame cùng một lúc
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self.stop_event.is_set():
                #gửi nhiệm vụ lấy frame với max_workers (3) luồng
                futures = [executor.submit(self._fetch_frame) for _ in range(self.max_workers)]
                for future in as_completed(futures):
                    frame = future.result()
                    #If a valid frame was fetched (not None), it's added to the frame buffer.
                    if frame is not None:
                        with self.lock:
                            self.frame_buffer.append(frame)

    def _fetch_frame(self):
        #take frame from the ESP32-CAM use http request
        try:
            response = requests.get(self.esp32_cam_url, timeout=1)
            if response.status_code == 200:
                #convert the response content to a numpy array and decode it to a frame
                img_array = np.frombuffer(response.content, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return frame
        except requests.exceptions.RequestException:
            pass
        return None

    def get_frame(self):
        with self.lock:
            return self.frame_buffer[-1] if self.frame_buffer else None

# YOLOv8-MultiPerson-Fall-Detection
An IoT-based multi-person fall detection system using YOLOv8 and ESP32-CAM. This project integrates advanced object detection with ESP32-CAM for real-time fall detection in multi-person environments, suitable for smart surveillance, healthcare, and security systems
## Project Description

This project focuses on real-time fall detection using an ESP32 device to capture and transmit images to a server, where Python scripts process the data for fall detection. The system is designed to monitor individuals and detect falls by analyzing human poses in real-time.

Key components of the project:
- **ESP32**: The ESP32 microcontroller captures images and streams them to a specific address over Wi-Fi.
- **YOLO Pose Detection**: A specialized model from the `ultralytics` library is used to detect and analyze human poses in each image frame.
- **Python**: Python scripts retrieve the image data from the specified address and apply pose detection algorithms to determine if a fall has occurred.
- **Flask**: A web framework that provides a simple interface for monitoring the real-time fall detection system and displaying results through a web page.
- **Multithreading**: Python's multithreading features are utilized to handle simultaneous tasks such as fetching image streams, running pose detection, and serving results via the web interface.

This project can be applied in environments such as elderly care facilities, hospitals, or smart homes where continuous monitoring for falls is essential. By combining edge computing with ESP32 and advanced pose detection algorithms, the system delivers an efficient, real-time solution for fall detection.
## Requirements

To run this project, you will need the following hardware and software:

### Hardware:
- **ESP32**: Used for capturing and streaming images over Wi-Fi.
- **Camera Module**: Integrated with the ESP32 to capture live images.
- **Computer or Server**: Running Python for image processing and fall detection.

### Software:
- **Python 3.x**: Make sure Python 3.x is installed on your system.
- **ESP32 Camera Library**: The appropriate library and setup to capture and stream images from the ESP32.

### How to Use the Project:
To use the projects, follow these steps:

1. **Clone the project from GitHub:**

   First, clone the repository to your local machine:

   ```bash
   git clone https://github.com/tonlongthuat/YOLOv8-MultiPerson-Fall-Detection.git

2. **Install dependencies:**
   
   To install the necessary Python libraries, run the following command:

   ```bash
    pip install -r requirements.txt

3. **Configure ESP32:**

Ensure that your ESP32 is set up with the correct firmware and libraries to capture images from a connected camera and stream them to the correct address.
These libraries are essential for enabling the camera functionality, connecting to Wi-Fi, and setting up the HTTP server to stream images.

After uploading the firmware to the ESP32, open the Serial Monitor in your Arduino IDE to retrieve the IP address assigned to your ESP32. This IP address will be crucial for integrating the camera feed with your Python code.

Once you have the IP address, make sure to replace the placeholder in your Python script with the actual IP address to ensure proper communication between the ESP32 and your Python application

## Credits

This project was developed by a dedicated team focused on creating an effective real-time fall detection system using the latest technologies in edge computing, computer vision, and IoT. Each member contributed significantly to the success of the project.

### Team Members:
- **[Tôn Long Thuật](https://github.com/tonlongthuat)**: Project Lead, responsible for coding the ESP32-CAM, writing Python code, implementing the fall detection algorithm, and managing the team.
- **[Nguyễn Việt Quang](https://github.com/ngvietquang)**: Web Developer, Responsible for developing the web interface for managing the camera systems, ensuring seamless integration and user-friendly interaction for real-time monitoring.
- **[Lê Quang Toàn](https://github.com/letoannn)**: Data Analyst – responsible for collecting and analyzing essential data throughout the project development process, providing insights that inform decision-making and improve system performance.


Special thanks to the open-source community for providing valuable resources such as the YOLO model and other essential Python libraries used in this project.

This project would not have been possible without the collective efforts of the entire team.


![GitHub contributors](https://img.shields.io/github/contributors/tonlongthuat/YOLOv8-MultiPerson-Fall-Detection)

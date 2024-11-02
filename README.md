# MultiPerson-Fall-Detection
![GitHub contributors](https://img.shields.io/github/contributors/tonlongthuat/YOLOv8-MultiPerson-Fall-Detection)

A robust, IoT-based fall detection system utilizing YOLOv11 and ESP32-CAM for real-time monitoring in multi-person environments. This project captures image streams from ESP32, processes them server-side with Python, and uses advanced detection algorithms to identify falls accurately. With real-time streaming and analysis, the system is well-suited for continuous monitoring in healthcare, eldercare, and security applications, ensuring efficient incident detection and response.
## Project Description

This system is designed to detect falls by capturing and analyzing live images transmitted from ESP32 to a server, leveraging the YOLOv11 object detection model. Unlike traditional pose-specific models, YOLOv11 excels in recognizing multiple individuals simultaneously, enhancing the accuracy of fall detection in crowded environments.

Key components of the project:
- **ESP32**: Streams image data over Wi-Fi to a server for processing.
- **YOLO Pose Detection**: Employs the `ultralytics` YOLOv11 model to detect and assess activity, allowing accurate identification of falls within the frame.
- **Python**: Manages image retrieval, fall detection algorithms, and data handling.
- **Flask**: Hosts a web interface for easy access to live monitoring and system outputs.
- **Multithreading**: Ensures seamless operation by handling tasks like data streaming, fall detection, and web service delivery concurrently.

This system combines edge computing with advanced detection algorithms to deliver efficient and reliable fall detection. Its capability to monitor multiple subjects simultaneously enhances safety in healthcare and residential settings, significantly improving response times and reducing fall-related risks.
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

   - **Module Requirements**: Ensure you are using the ESP32 AI Thinker module for compatibility.

   - **Library Installation**: Install the necessary libraries by including the following in your Arduino IDE:

     ```cpp
     #include <WiFi.h>
     #include <esp_camera.h>
     #include <WebServer.h>
     ```

   - **Wi-Fi Credentials**: Modify the user credentials in your code as follows:

     ```cpp
     const char* ssid = "YOUR_SSID";
     const char* password = "YOUR_PASSWORD";
     ```

   - **Firmware Upload**: Upload your firmware using the Arduino IDE. Open the Serial Monitor (baud rate 115200) to obtain the assigned IP address.

   - **Python Integration**: Update your Python script to replace the placeholder IP address with the ESP32's actual IP address to ensure communication.


## Credits

This project was developed by a dedicated team focused on creating an effective real-time fall detection system using the latest technologies in edge computing, computer vision, and IoT. Each member contributed significantly to the success of the project.

### Team Members:
- **[Tôn Long Thuật](https://github.com/tonlongthuat)**: Project Lead, directing technical strategy, configuring and integrating the ESP32-CAM, refining the fall detection algorithm, developing Python code for real-time data processing, ensuring cross-functional alignment, and delivering high-quality, timely outcomes.
- **[Nguyễn Việt Quang](https://github.com/ngvietquang)**: Web Developer, Responsible for developing the web interface for managing the camera systems, ensuring seamless integration and user-friendly interaction for real-time monitoring.
- **[Lê Quang Toàn](https://github.com/letoannn)**: Data Analyst – responsible for collecting and analyzing essential data throughout the project development process, providing insights that inform decision-making and improve system performance.


Special thanks to the open-source community for providing valuable resources such as the YOLO model and other essential Python libraries used in this project.

This project would not have been possible without the collective efforts of the entire team.
### ⭐ Support This Project

If you find this project useful or interesting, please consider giving it a star! Your support helps improve visibility and encourages further development.

Thank you for your interest!

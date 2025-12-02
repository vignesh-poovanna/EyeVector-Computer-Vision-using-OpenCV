#  EyeVector

EyeVector is a real-time eye tracking application that uses computer vision to detect blinks, track gaze direction, and control system audio through double-blink gestures. Built with Python, OpenCV, and dlib.

##  Features

- **Blink Detection**: Automatically detects and counts eye blinks using facial landmark detection
- **Gaze Tracking**: Tracks eye gaze direction (Left, Right, Center) in real-time
- **Audio Control**: Double-blink to toggle mute/unmute system audio
- **Fatigue Alert**: Alerts when eyes are closed for more than 3 seconds
- **Session Summary**: Displays detailed statistics after each tracking session
- **Modern GUI**: Clean and intuitive tkinter-based user interface

##  Requirements

- Python 3.7+
- Webcam/Camera
- Windows OS (for audio control functionality)

##  Dependencies

```
opencv-python
dlib
numpy
scipy
imutils
pycaw
comtypes
tkinter (usually included with Python)
```

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/EyeVector.git
cd EyeVector
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install opencv-python dlib numpy scipy imutils pycaw comtypes
```

**Note**: Installing `dlib` on Windows may require additional steps. If you encounter issues, you may need to:
- Install CMake: `pip install cmake`
- Install Visual C++ Build Tools
- Or download pre-built wheels from [here](https://github.com/z-mahmud22/D Lib_Windows_Python3.x_Prebuilt_file)

### 3. Download the facial landmark predictor

Download the `shape_predictor_68_face_landmarks.dat` file from:
- [dlib's models repository](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

Extract it and place it in the project directory (same folder as `eyevector.py`).

Alternatively, if you already have the file, ensure it's named exactly: `shape_predictor_68_face_landmarks.dat`

##  Usage

### Running the Application

1. Launch the application:
```bash
python eyevector.py
```

2. Click the **"Start Webcam"** button in the GUI window

3. Position yourself in front of the camera - make sure your face is clearly visible

4. The application will display:
   - Blink count in real-time
   - Current gaze direction for each eye
   - Current mute/unmute status
   - Eye outlines overlaid on the video feed

### Controls

- **Double Blink**: Mute/unmute system audio (must be within 0.7 seconds, with 1.5 second cooldown)
- **Press 'q'**: Quit the tracking session and return to the main window
- **Close Window**: Exit the application

### Session Summary

After closing a tracking session (by pressing 'q'), a summary will be displayed showing:
- Session start and end times
- Total number of blinks detected
- Final gaze direction for left and right eyes
- Final mute/unmute status

##  How It Works

1. **Face Detection**: Uses dlib's frontal face detector to locate faces in the video stream
2. **Landmark Detection**: Extracts 68 facial landmarks, focusing on eye regions
3. **Eye Aspect Ratio (EAR)**: Calculates the aspect ratio of each eye to detect blinks
4. **Gaze Direction**: Analyzes the distribution of white pixels (pupils) in each eye region
5. **Double Blink Detection**: Monitors blink timing to detect rapid consecutive blinks
6. **Audio Control**: Uses Windows COM interfaces (via pycaw) to control system audio

##  Notes

- Works best in well-lit environments
- Ensure your face is clearly visible and centered in the camera frame
- The application requires Windows for audio control features
- For best results, sit approximately 1-2 feet from your webcam

##  Troubleshooting

**Issue**: "Could not toggle mute" error
- **Solution**: Ensure you're running on Windows and have administrator privileges if needed

**Issue**: dlib installation fails
- **Solution**: Install CMake first, or use pre-built wheels for Windows

**Issue**: Camera not detected
- **Solution**: Check that your webcam is connected and not being used by another application

**Issue**: "shape_predictor_68_face_landmarks.dat not found"
- **Solution**: Download the file from the dlib models repository and place it in the project directory

##  License

This project is open source and available under the [MIT License](LICENSE).


##  Acknowledgments

- dlib library for facial landmark detection
- OpenCV for computer vision capabilities
- pycaw for Windows audio control

---

⭐ If you find this project useful, please consider giving it a star!


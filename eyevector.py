import cv2
import dlib
import numpy as np
import time
from scipy.spatial import distance as dist
from imutils import face_utils
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
from comtypes import CLSCTX_ALL
import tkinter as tk
from tkinter import messagebox

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def get_gaze_direction_and_ratio(eye_points, facial_landmarks, gray):
    eye_region = np.array([(facial_landmarks.part(p).x, facial_landmarks.part(p).y) for p in eye_points], np.int32)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.polylines(mask, [eye_region], True, 255, 1)
    cv2.fillPoly(mask, [eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)
    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])
    gray_eye = eye[min_y:max_y, min_x:max_x]
    if gray_eye.size == 0:
        return "Center", 1.0
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    h, w = threshold_eye.shape
    left_white = cv2.countNonZero(threshold_eye[:, 0:int(w / 2)])
    right_white = cv2.countNonZero(threshold_eye[:, int(w / 2):w])
    if left_white == 0:
        gaze_ratio = 1
    elif right_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_white / right_white
    if gaze_ratio < 0.8:
        gaze_dir = "Right"
    elif gaze_ratio > 1.2:
        gaze_dir = "Left"
    else:
        gaze_dir = "Center"
    return gaze_dir, gaze_ratio

def toggle_mute():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        volume.SetMute(not volume.GetMute(), None)
        mstate = "Muted" if volume.GetMute() else "Unmuted"
        print(f"[+] Volume {mstate}")
    except Exception as e:
        print("[!] Could not toggle mute.", e)

def get_mute_status():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        return volume.GetMute()
    except:
        return None

#  GUI LOGIC 

class EyeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg='#D6EAF8')
        self.title("EyeVector")
        self.geometry("470x410")
        self.session_info = None
        
        self.header = tk.Label(self, text="EyeVector", font=("Helvetica", 22, "bold"), bg="#5DADE2", fg="white", pady=10)
        self.header.pack(fill=tk.X)
        self.sub = tk.Label(self, text="Detect Blinks, Gaze & Double Blink to Mute/Unmute\n", 
                            font=("Helvetica", 14), bg="#D6EAF8")
        self.sub.pack()
        self.button = tk.Button(self, text='Start Webcam', font=('Helvetica', 16, 'bold'), bg='#48C9B0', fg='white', command=self.run_tracking, padx=20, pady=10)
        self.button.pack(pady=30)
        self.summary_label = tk.Label(self, text="", font=("Arial", 13), bg="#D6EAF8", fg="#154360", justify='left', anchor="nw")
        self.summary_label.pack(pady=10)
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def run_tracking(self):
        self.summary_label.config(text="")
        self.button.config(state='disabled')
        self.session_info = self.run_eye_tracker()
        self.display_summary()
        self.button.config(state='normal')

    def display_summary(self):
        if self.session_info:
            text = (
                f"\nSession Summary\n\n"
                f"Session started: {self.session_info['start']}\n"
                f"Session ended:   {self.session_info['end']}\n"
                f"Total blinks:    {self.session_info['total_blinks']}\n"
                f"Gaze (left/right): {self.session_info['left_gaze']} / {self.session_info['right_gaze']}\n"
                f"Mute/Unmute status: {self.session_info['mute_state']}\n"
            )
            self.summary_label.config(text=text)
        else:
            self.summary_label.config(text="")

    def close_app(self):
        self.destroy()

    def run_eye_tracker(self):
        # --- Eye Tracker Logic ---
        EYE_AR_THRESH = 0.23
        EYE_AR_CONSEC_FRAMES = 2
        DOUBLE_BLINK_WINDOW = 0.7
        DOUBLE_BLINK_COOLDOWN = 1.5

        COUNTER = 0
        TOTAL = 0
        ALERT_SHOWN = False
        eye_closed_start_time = None

        last_blink_time = None
        last_toggle_time = 0

        session_start = time.strftime("%Y-%m-%d %H:%M:%S")
        session_end = None
        gaze_left_final = "Center"
        gaze_right_final = "Center"

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        cap = cv2.VideoCapture(0)
        print("Double Blink = Mute/Unmute | Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            for rect in rects:
                shape = predictor(gray, rect)
                leftEye = face_utils.shape_to_np(shape)[lStart:lEnd]
                rightEye = face_utils.shape_to_np(shape)[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0

                # Thin green outlines
                cv2.drawContours(frame, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)

                current_time = time.time()
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    if eye_closed_start_time is None:
                        eye_closed_start_time = current_time
                    time_closed = current_time - eye_closed_start_time
                    if time_closed > 3:
                        ALERT_SHOWN = True
                else:
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
                        # Improved double blink detection
                        if last_blink_time is not None:
                            since_last = current_time - last_blink_time
                            since_toggle = current_time - last_toggle_time
                            if since_last < DOUBLE_BLINK_WINDOW and since_toggle > DOUBLE_BLINK_COOLDOWN:
                                toggle_mute()
                                last_toggle_time = current_time
                                last_blink_time = None
                            else:
                                last_blink_time = current_time
                        else:
                            last_blink_time = current_time
                    COUNTER = 0
                    eye_closed_start_time = None
                    ALERT_SHOWN = False

                gaze_left, ratio_left = get_gaze_direction_and_ratio(range(lStart, lEnd), shape, gray)
                gaze_right, ratio_right = get_gaze_direction_and_ratio(range(rStart, rEnd), shape, gray)
                gaze_left_final = gaze_left
                gaze_right_final = gaze_right

                mute_state = get_mute_status()
                mute_txt = "Muted" if mute_state == 1 else "Unmuted"

                cv2.putText(frame, f"Blinks: {TOTAL}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Gaze: {gaze_left}/{gaze_right}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"Mute: {mute_txt}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Double Blink = Mute Toggle", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)
                if ALERT_SHOWN:
                    cv2.putText(frame, "ALERT: Eyes closed > 3s!", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

            cv2.imshow("Blink & Gaze Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                session_end = time.strftime("%Y-%m-%d %H:%M:%S")
                break

        cap.release()
        cv2.destroyAllWindows()

        return {
            "start": session_start,
            "end": session_end,
            "total_blinks": TOTAL,
            "left_gaze": gaze_left_final,
            "right_gaze": gaze_right_final,
            "mute_state": mute_txt
        }

# ---------------- MAIN -----------------
if __name__ == "__main__":
    app = EyeTrackerApp()
    app.mainloop()

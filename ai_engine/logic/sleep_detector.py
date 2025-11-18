import cv2
import mediapipe as mp
import math
import time

mp_face_mesh = mp.solutions.face_mesh

# Eye landmark indices (MediaPipe Face Mesh)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def euclidean_dist(p1, p2):
    return math.dist(p1, p2)


def eye_aspect_ratio(landmarks, eye_points):
    top = euclidean_dist(landmarks[eye_points[1]], landmarks[eye_points[2]])
    bottom = euclidean_dist(landmarks[eye_points[4]], landmarks[eye_points[5]])
    width = euclidean_dist(landmarks[eye_points[0]], landmarks[eye_points[3]])
    return (top + bottom) / (2.0 * width)


class SleepDetector:
    def __init__(self):
        self.sleep_start = None
        self.sleeping = False

        # Improved thresholds for better accuracy
        self.threshold = 0.25  # Lower = more sensitive (was 0.35)
        self.min_sleep_time = 3  # Require 3 seconds (was 2)

        # Blink detection to avoid false positives
        self.blink_threshold = 0.15  # Very low EAR = blink
        self.last_blink_time = 0
        self.blink_cooldown = 0.5  # Ignore detections 0.5s after blink

        # Confirmation buffer
        self.closed_eye_buffer = []
        self.buffer_size = 10  # Need 10 consecutive frames

        self.face = None

    def setup(self):
        """Initialize face mesh with optimized settings"""
        self.face = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,  # Higher confidence
            min_tracking_confidence=0.5
        )

    def detect(self, frame):
        """Detect sleeping with improved accuracy"""
        h, w = frame.shape[:2]

        results = self.face.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # If no face detected, reset state
        if not results.multi_face_landmarks:
            self.sleeping = False
            self.sleep_start = None
            self.closed_eye_buffer.clear()
            return False

        for face in results.multi_face_landmarks:
            # Convert landmarks to pixel locations
            landmarks = [(int(l.x * w), int(l.y * h)) for l in face.landmark]

            # Calculate EAR for both eyes
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
            ear = (left_ear + right_ear) / 2

            current_time = time.time()

            # Detect blink (very quick eye closure)
            if ear < self.blink_threshold:
                self.last_blink_time = current_time
                self.closed_eye_buffer.clear()
                return False

            # Ignore detections shortly after blink
            if current_time - self.last_blink_time < self.blink_cooldown:
                return False

            # Eyes closed check with buffer
            eyes_closed = ear < self.threshold

            # Add to buffer
            self.closed_eye_buffer.append(eyes_closed)
            if len(self.closed_eye_buffer) > self.buffer_size:
                self.closed_eye_buffer.pop(0)

            # Need consistent closed eyes
            if len(self.closed_eye_buffer) >= self.buffer_size:
                confirmed_closed = sum(self.closed_eye_buffer) >= (self.buffer_size * 0.8)

                if confirmed_closed:
                    if not self.sleeping:
                        self.sleep_start = current_time
                        self.sleeping = True
                else:
                    self.sleeping = False
                    self.sleep_start = None

            # Require sustained sleeping
            if self.sleeping and self.sleep_start:
                sleep_duration = current_time - self.sleep_start
                if sleep_duration >= self.min_sleep_time:
                    return True

        return False
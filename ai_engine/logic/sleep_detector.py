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
        self.threshold = 0.35  # EAR threshold (can adjust later)
        self.min_sleep_time = 2  # seconds required to count as sleeping
        self.face = None  # Face mesh will be initialized in setup()

    def setup(self):
        # More sensitive detection settings for low-light or low-quality webcams
        self.face = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        )

    def detect(self, frame):
        h, w = frame.shape[:2]

        results = self.face.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # If no face detected, return False (not sleeping)
        if not results.multi_face_landmarks:
            # Reset sleeping state if no face detected
            self.sleeping = False
            self.sleep_start = None
            return False

        for face in results.multi_face_landmarks:

            # Convert landmarks to pixel locations
            landmarks = [(int(l.x * w), int(l.y * h)) for l in face.landmark]

            # EAR calculation for both eyes
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
            ear = (left_ear + right_ear) / 2

            # Eyes closed?
            if ear < self.threshold:
                if not self.sleeping:
                    self.sleep_start = time.time()
                    self.sleeping = True
            else:
                self.sleeping = False
                self.sleep_start = None

            # Sleeping for required time
            if self.sleeping and self.sleep_start and time.time() - self.sleep_start >= self.min_sleep_time:
                return True

        return False
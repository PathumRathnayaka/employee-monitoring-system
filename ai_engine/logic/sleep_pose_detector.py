import mediapipe as mp
import math

mp_pose = mp.solutions.pose

class SleepPoseDetector:
    def __init__(self):
        self.pose = mp_pose.Pose(min_detection_confidence=0.5,
                                 min_tracking_confidence=0.5)

    def detect(self, frame):
        h, w = frame.shape[:2]
        results = self.pose.process(frame)

        if not results.pose_landmarks:
            return False

        lm = results.pose_landmarks.landmark

        # Extract key points
        nose = lm[0]
        left_shoulder = lm[11]
        right_shoulder = lm[12]

        # Convert to pixel coordinates
        nose_y = nose.y * h
        shoulder_y = ((left_shoulder.y + right_shoulder.y) / 2) * h

        # If head is LOWER than shoulder → sleeping on table
        if nose_y > shoulder_y:
            return True

        return False

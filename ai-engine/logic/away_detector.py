import time

class AwayDetector:
    def __init__(self):
        self.last_seen_time = time.time()
        self.away_threshold = 3   # seconds before marking as away

    def update(self, person_detected):
        """ person_detected = True/False from YOLO """

        current_time = time.time()

        if person_detected:
            self.last_seen_time = current_time
            return False  # not away

        # If no person detected for long enough → away
        if current_time - self.last_seen_time > self.away_threshold:
            return True

        return False

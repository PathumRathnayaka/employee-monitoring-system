import time


class AwayDetector:
    def __init__(self):
        self.last_seen_time = time.time()
        self.away_threshold = 5  # Increased from 3 to 5 seconds

        # Confirmation buffer
        self.person_buffer = []
        self.buffer_size = 10  # Need 10 frames of consistent data
        self.currently_away = False

    def update(self, person_detected):
        """
        person_detected = True/False from YOLO
        Returns True if person is away from desk
        """
        current_time = time.time()

        # Add to confirmation buffer
        self.person_buffer.append(person_detected)
        if len(self.person_buffer) > self.buffer_size:
            self.person_buffer.pop(0)

        # Need consistent detection
        if len(self.person_buffer) >= self.buffer_size:
            # Majority voting
            confirmed_present = sum(self.person_buffer) >= (self.buffer_size * 0.6)

            if confirmed_present:
                self.last_seen_time = current_time

                # If was away, now returned
                if self.currently_away:
                    self.currently_away = False
                    return False

                return False
            else:
                # Person not consistently detected
                time_away = current_time - self.last_seen_time

                if time_away > self.away_threshold:
                    self.currently_away = True
                    return True
        else:
            # Not enough data yet
            if person_detected:
                self.last_seen_time = current_time

        return self.currently_away
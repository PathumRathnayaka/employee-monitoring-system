import json
import os
from datetime import datetime, timedelta

EVENT_LOG_PATH = "data/events"

class SummaryGenerator:

    def _load_events(self, employee_id, date):
        filename = f"{EVENT_LOG_PATH}/{date}_{employee_id}.json"

        if not os.path.exists(filename):
            return []

        with open(filename, "r") as f:
            return json.load(f)

    def _calculate_time(self, events, event_type):
        """
        Calculate total time for a given event type ("sleep", "phone", "away")
        """

        start_time = None
        total_duration = timedelta()

        for event in events:
            if event["event_type"] == event_type:

                if event["status"] == "start":
                    start_time = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")

                if event["status"] == "end" and start_time:
                    end_time = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
                    total_duration += (end_time - start_time)
                    start_time = None

        return total_duration

    def generate_summary(self, employee_id="001"):
        date = datetime.now().strftime("%Y-%m-%d")
        events = self._load_events(employee_id, date)

        if not events:
            return {
                "date": date,
                "message": "No events recorded today",
                "sleep_minutes": 0,
                "phone_minutes": 0,
                "away_minutes": 0,
                "productive_minutes": 0,
                "productivity_score": 0
            }

        # Calculate durations
        sleep_time = self._calculate_time(events, "sleep")
        phone_time = self._calculate_time(events, "phone")
        away_time = self._calculate_time(events, "away")

        total_day_minutes = 12 * 60  # assume 12h monitoring window
        total_nonproductive = (sleep_time + phone_time + away_time).total_seconds() / 60
        productive_minutes = total_day_minutes - total_nonproductive

        productivity_score = max(0, round((productive_minutes / total_day_minutes) * 100))

        return {
            "date": date,
            "sleep_minutes": round(sleep_time.total_seconds() / 60),
            "phone_minutes": round(phone_time.total_seconds() / 60),
            "away_minutes": round(away_time.total_seconds() / 60),
            "productive_minutes": round(productive_minutes),
            "productivity_score": productivity_score
        }

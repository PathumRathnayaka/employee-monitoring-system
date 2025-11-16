from datetime import datetime, timedelta
from backend.database import events_collection

class SummaryGenerator:

    def generate_summary(self, employee_id="001"):
        today = datetime.now().date()

        # Fetch all today's events from DB
        events = list(events_collection.find({
            "employee_id": employee_id,
            "timestamp": {
                "$gte": datetime(today.year, today.month, today.day),
                "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
            }
        }))

        if not events:
            return {
                "date": str(today),
                "message": "No events recorded today",
                "sleep_minutes": 0,
                "phone_minutes": 0,
                "away_minutes": 0,
                "productive_minutes": 0,
                "productivity_score": 0
            }

        def calc_time(event_type):
            start = None
            duration = timedelta()

            for e in events:
                if e["event_type"] == event_type:
                    if e["status"] == "start":
                        start = e["timestamp"]
                    elif e["status"] == "end" and start:
                        duration += (e["timestamp"] - start)
                        start = None

            return duration

        sleep_time = calc_time("sleep")
        phone_time = calc_time("phone")
        away_time = calc_time("away")

        total_day = timedelta(hours=12)
        nonproductive = sleep_time + phone_time + away_time
        productive = max(timedelta(), total_day - nonproductive)

        productivity_score = int((productive / total_day) * 100)

        return {
            "date": str(today),
            "sleep_minutes": round(sleep_time.total_seconds() / 60),
            "phone_minutes": round(phone_time.total_seconds() / 60),
            "away_minutes": round(away_time.total_seconds() / 60),
            "productive_minutes": round(productive.total_seconds() / 60),
            "productivity_score": productivity_score
        }

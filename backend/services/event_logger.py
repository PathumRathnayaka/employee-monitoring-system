from datetime import datetime
from backend.database import events_collection

class EventLogger:
    def __init__(self, employee_id="001"):
        self.employee_id = employee_id
        self.current_events = {
            "sleep": False,
            "phone": False,
            "away": False
        }

    def _write_event(self, event_type, status):
        event = {
            "employee_id": self.employee_id,
            "event_type": event_type,
            "status": status,
            "timestamp": datetime.now()
        }

        events_collection.insert_one(event)

        print(f"[EVENT → DB] {event_type} - {status}")

    def handle_event(self, event_type, active):
        prev = self.current_events[event_type]

        if active and not prev:
            self._write_event(event_type, "start")

        elif not active and prev:
            self._write_event(event_type, "end")

        self.current_events[event_type] = active

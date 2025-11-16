import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

EVENT_LOG_PATH = os.path.join(BASE_DIR, "data", "events")

class EventLogger:
    def __init__(self, employee_id="001"):
        self.employee_id = employee_id
        self.current_events = {
            "sleep": False,
            "phone": False,
            "away": False
        }

    def _write_event(self, event_type, status):
        """
        event_type: sleep / phone / away
        status: start/end
        """
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"{EVENT_LOG_PATH}/{today}_{self.employee_id}.json"

        # Ensure folder exists
        os.makedirs(EVENT_LOG_PATH, exist_ok=True)

        # If file does not exist, create empty list
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump([], f)

        # Load existing events
        with open(filepath, "r") as f:
            events = json.load(f)

        event = {
            "event_type": event_type,
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        events.append(event)

        # Save updated file
        with open(filepath, "w") as f:
            json.dump(events, f, indent=4)

        print(f"[EVENT] {event_type} - {status}")

    def handle_event(self, event_type, active):
        previous_state = self.current_events[event_type]

        if active and not previous_state:
            # Event started
            self._write_event(event_type, "start")

        elif not active and previous_state:
            # Event ended
            self._write_event(event_type, "end")

        # Update state
        self.current_events[event_type] = active

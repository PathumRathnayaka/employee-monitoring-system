from datetime import datetime
from backend.database import events_collection
import backend.socket_instance as socket_instance
import time


class EventLogger:

    def __init__(self, employee_id="001"):
        self.employee_id = employee_id
        self.current_events = {
            "sleep": False,
            "phone": False,
            "away": False
        }

        # Batch update settings - emit to dashboard every 5 seconds instead of real-time
        self.last_emit_time = time.time()
        self.emit_interval = 5  # seconds
        self.pending_updates = []

    def _emit_batch_updates(self, force=False):
        """Emit batched updates to dashboard every N seconds"""
        current_time = time.time()

        # Only emit if interval passed or forced
        if force or (current_time - self.last_emit_time >= self.emit_interval):
            socketio = socket_instance.get_socketio()
            if socketio and self.current_events:
                # Send current state as batch update
                data = {
                    "sleep": self.current_events["sleep"],
                    "phone": self.current_events["phone"],
                    "away": self.current_events["away"],
                    "timestamp": datetime.now().isoformat()
                }
                print(f"[BATCH UPDATE] {data}")
                socketio.emit("status_batch_update", data)
                self.last_emit_time = current_time

    def _write_event(self, event_type, status):
        """Write event to database"""
        event = {
            "employee_id": self.employee_id,
            "event_type": event_type,
            "status": status,
            "timestamp": datetime.now()
        }

        events_collection.insert_one(event)
        print(f"[EVENT → DB] {event_type} - {status}")

    def handle_event(self, event_type, active):
        """Handle state changes and log events (no immediate socket emission)"""
        previous = self.current_events[event_type]

        # Only write when state changes
        if active and not previous:
            self._write_event(event_type, "start")
            self.current_events[event_type] = True

        elif not active and previous:
            self._write_event(event_type, "end")
            self.current_events[event_type] = False

        # Batch emit updates (not real-time)
        self._emit_batch_updates()

    def force_emit(self):
        """Force emit current state to dashboard"""
        self._emit_batch_updates(force=True)
from datetime import datetime
from backend.database import events_collection
import backend.socket_instance as socket_instance


class EventLogger:

    def __init__(self, employee_id="001"):
        self.employee_id = employee_id
        self.current_events = {
            "sleep": False,
            "phone": False,
            "away": False
        }

    def _emit_realtime(self, event_type, active):
        """Emit real-time status update via SocketIO"""
        socketio = socket_instance.get_socketio()
        if socketio:
            data = {
                "event_type": event_type,
                "active": active,
                "timestamp": datetime.now().isoformat()
            }
            print(f"[SOCKET EMIT] {data}")  # Debug log
            socketio.emit("status_update", data)
        else:
            print("[WARNING] SocketIO not initialized!")

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
        """Handle state changes and emit/log events"""
        previous = self.current_events[event_type]

        # Only write when state changes
        if active and not previous:
            self._write_event(event_type, "start")
            self._emit_realtime(event_type, True)

        elif not active and previous:
            self._write_event(event_type, "end")
            self._emit_realtime(event_type, False)

        self.current_events[event_type] = active
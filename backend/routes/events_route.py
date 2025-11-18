from flask import Blueprint, jsonify
from datetime import datetime
from backend.database import events_collection

events_bp = Blueprint("events", __name__)


@events_bp.get("/events/today/<employee_id>")
def get_today_events(employee_id):
    """Get all events for today from MongoDB"""
    today = datetime.now().date()

    # Query MongoDB for today's events
    events = list(events_collection.find({
        "employee_id": employee_id,
        "timestamp": {
            "$gte": datetime(today.year, today.month, today.day),
            "$lt": datetime(today.year, today.month, today.day + 1)
        }
    }, {"_id": 0}))  # Exclude MongoDB _id field

    # Convert datetime objects to ISO format strings
    for event in events:
        if isinstance(event.get("timestamp"), datetime):
            event["timestamp"] = event["timestamp"].isoformat()

    return jsonify(events)


@events_bp.get("/events/live/<employee_id>")
def get_live_status(employee_id):
    """
    Returns the last known current state (sleep/phone/away)
    based on the most recent events in the database
    """
    today = datetime.now().date()

    # Get all today's events
    events = list(events_collection.find({
        "employee_id": employee_id,
        "timestamp": {
            "$gte": datetime(today.year, today.month, today.day),
            "$lt": datetime(today.year, today.month, today.day + 1)
        }
    }).sort("timestamp", -1))  # Sort by timestamp descending

    # Initialize status
    live_state = {"sleep": False, "phone": False, "away": False}

    # Process events to determine current state
    # We need to find the most recent start/end for each event type
    event_states = {}

    for event in reversed(events):  # Process in chronological order
        event_type = event["event_type"]
        status = event["status"]

        if status == "start":
            event_states[event_type] = True
        elif status == "end":
            event_states[event_type] = False

    # Update live_state with the latest states
    for event_type, is_active in event_states.items():
        if event_type in live_state:
            live_state[event_type] = is_active

    return jsonify(live_state)
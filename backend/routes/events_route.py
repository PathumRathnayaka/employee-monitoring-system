from flask import Blueprint, jsonify
import os, json
from datetime import datetime

events_bp = Blueprint("events", __name__)

EVENT_LOG_PATH = "data/events"


@events_bp.get("/events/today/<employee_id>")
def get_today_events(employee_id):

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{EVENT_LOG_PATH}/{today}_{employee_id}.json"

    if not os.path.exists(filepath):
        return jsonify({"status": "no events found"})

    with open(filepath, "r") as f:
        events = json.load(f)

    return jsonify(events)


@events_bp.get("/events/live/<employee_id>")
def get_live_status(employee_id):
    """
    Returns the last known current state (sleep/phone/away)
    """

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{EVENT_LOG_PATH}/{today}_{employee_id}.json"

    if not os.path.exists(filepath):
        return jsonify({
            "sleep": False,
            "phone": False,
            "away": False
        })

    with open(filepath, "r") as f:
        events = json.load(f)

    live_state = {"sleep": False, "phone": False, "away": False}

    for e in events:
        if e["status"] == "start":
            live_state[e["event_type"]] = True
        if e["status"] == "end":
            live_state[e["event_type"]] = False

    return jsonify(live_state)

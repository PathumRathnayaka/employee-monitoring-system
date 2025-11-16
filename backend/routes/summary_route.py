from flask import Blueprint, jsonify
from backend.services.summary_generator import SummaryGenerator

summary_bp = Blueprint("summary", __name__)
sg = SummaryGenerator()

@summary_bp.get("/summary/today/<employee_id>")
def today_summary(employee_id):
    summary = sg.generate_summary(employee_id)
    return jsonify(summary)

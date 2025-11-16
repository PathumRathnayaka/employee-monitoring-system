from flask import Flask
from backend.routes.events_route import events_bp
from backend.routes.summary_route import summary_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(events_bp)
app.register_blueprint(summary_bp)

@app.get("/")
def home():
    return {"status": "backend running", "message": "Employee Monitoring API"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import routes after socketio is created to avoid circular imports
from backend.routes.events_route import events_bp
from backend.routes.summary_route import summary_bp

app.register_blueprint(events_bp)
app.register_blueprint(summary_bp)


@app.get("/")
def home():
    return {"status": "backend running"}


if __name__ == "__main__":
    print("🚀 Starting Flask-SocketIO server on http://127.0.0.1:5000")
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

from backend.routes.events_route import events_bp
from backend.routes.summary_route import summary_bp

app.register_blueprint(events_bp)
app.register_blueprint(summary_bp)


@app.get("/")
def home():
    return {"status": "backend running"}


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)

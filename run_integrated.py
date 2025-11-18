"""
Integrated runner: Starts both Flask backend and AI detection together
This ensures the socketio instance is properly shared
"""
import sys
import time

# Import Flask app and socketio
from backend.app import app, socketio
import backend.socket_instance as socket_instance

# Import detector
from ai_engine.detector import start_detection_headless


def start_backend():
    """Start Flask-SocketIO server"""
    print("=" * 60)
    print("🚀 Starting Employee Monitoring System")
    print("=" * 60)
    print("📡 Backend Server: http://127.0.0.1:5000")
    print("🔌 WebSocket: Enabled")
    print("📹 AI Detection: Starting...")
    print("=" * 60)

    # Initialize the global socketio instance
    socket_instance.init_socketio(socketio)

    # Start AI detection in background thread
    print("\n⏳ Initializing AI Engine...")
    detection_thread = start_detection_headless()
    time.sleep(2)  # Give camera time to initialize
    print("✅ AI Engine running in background\n")

    # Start Flask server
    socketio.run(
        app,
        debug=False,  # Set to False to avoid double initialization
        port=5000,
        host='0.0.0.0',
        allow_unsafe_werkzeug=True,
        use_reloader=False  # Disable reloader to prevent double start
    )


if __name__ == "__main__":
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        sys.exit(0)
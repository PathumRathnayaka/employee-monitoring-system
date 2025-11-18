"""
Run the Flask backend server with SocketIO
"""
from backend.app import app, socketio
import backend.socket_instance as socket_instance

# Initialize the global socketio instance
socket_instance.init_socketio(socketio)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting Employee Monitoring Backend")
    print("📡 Server: http://127.0.0.1:5000")
    print("🔌 WebSocket: Enabled")
    print("=" * 50)

    socketio.run(
        app,
        debug=True,
        port=5000,
        host='0.0.0.0',
        allow_unsafe_werkzeug=True
    )
"""
Integrated runner: Starts both Flask backend and AI detection together
Camera window runs in main thread, Flask runs in background thread
"""
import sys
import time
import threading

# Import Flask app and socketio
from backend.app import app, socketio
import backend.socket_instance as socket_instance

# Import detector
from ai_engine.detector import DetectionRunner


def start_flask_server():
    """Start Flask-SocketIO server in background thread"""
    socketio.run(
        app,
        debug=False,
        port=5000,
        host='0.0.0.0',
        allow_unsafe_werkzeug=True,
        use_reloader=False
    )


def start_backend_with_camera():
    """Start system with camera window in main thread"""
    print("=" * 60)
    print("🚀 Starting Employee Monitoring System")
    print("=" * 60)
    print("📡 Backend Server: http://127.0.0.1:5000")
    print("🔌 WebSocket: Enabled")
    print("📹 AI Detection: Starting...")
    print("🎥 Camera Preview: Enabled")
    print("=" * 60)

    # Initialize the global socketio instance
    socket_instance.init_socketio(socketio)

    # Start Flask in background thread
    print("\n⏳ Starting Flask server in background...")
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    time.sleep(2)  # Give Flask time to start
    print("✅ Flask server running\n")

    # Initialize detector
    print("⏳ Initializing AI Engine with Camera...")
    detector = DetectionRunner(show_preview=True)
    detector.start()
    time.sleep(1)

    print("✅ AI Engine running with camera preview\n")
    print("💡 Camera Window Controls:")
    print("   • Green boxes: Detected objects")
    print("   • Yellow boxes: Active phone usage")
    print("   • Red banner: Sleeping detected")
    print("   • Yellow banner: Phone usage detected")
    print("   • Blue banner: Away from desk")
    print("   • Press 'q' in camera window to close and exit\n")
    print("=" * 60)
    print("🎥 Camera window should open now...")
    print("=" * 60 + "\n")

    # Run camera loop in main thread (required for OpenCV window)
    try:
        detector.run_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    finally:
        detector.stop()


def start_backend_headless():
    """Start system without camera window"""
    print("=" * 60)
    print("🚀 Starting Employee Monitoring System (Headless Mode)")
    print("=" * 60)
    print("📡 Backend Server: http://127.0.0.1:5000")
    print("🔌 WebSocket: Enabled")
    print("📹 AI Detection: Background only")
    print("=" * 60)

    # Initialize the global socketio instance
    socket_instance.init_socketio(socketio)

    # Initialize detector in headless mode
    print("\n⏳ Initializing AI Engine...")
    detector = DetectionRunner(show_preview=False)
    detector.start()

    detection_thread = threading.Thread(target=detector.run_headless, daemon=True)
    detection_thread.start()
    time.sleep(2)

    print("✅ AI Engine running in background\n")

    # Run Flask in main thread
    socketio.run(
        app,
        debug=False,
        port=5000,
        host='0.0.0.0',
        allow_unsafe_werkzeug=True,
        use_reloader=False
    )


if __name__ == "__main__":
    # Check command line arguments
    show_camera = "--no-camera" not in sys.argv

    try:
        if show_camera:
            start_backend_with_camera()
        else:
            start_backend_headless()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        sys.exit(0)
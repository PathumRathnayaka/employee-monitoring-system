# This file holds the socketio instance to avoid circular imports
socketio = None

def init_socketio(sio):
    """Initialize the global socketio instance"""
    global socketio
    socketio = sio

def get_socketio():
    """Get the global socketio instance"""
    return socketio
from flask_socketio import SocketIO

socketio = SocketIO()

socketio.on('connect')
def connected_clients():
    print("Socket connected")
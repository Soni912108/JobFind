from flask_socketio import SocketIO
from flask_mail import Mail
from flask import current_app

# extensions
mail = Mail()
socketio = SocketIO()

socketio.on('connect')
def connected_clients():
    current_app.logger.info("Socket connected")
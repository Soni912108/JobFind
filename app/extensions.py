from flask_socketio import SocketIO
from flask_mail import Mail
from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Instantiate the limiter
limiter = Limiter(
    get_remote_address,  # default: rate-limit by client IP
    app=current_app,
    default_limits=["200 per day", "50 per hour"]
)

# extensions
mail = Mail()
socketio = SocketIO()

socketio.on('connect')
def connected_clients():
    current_app.logger.info("Socket connected")
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .extensions import socketio

from dotenv import load_dotenv
import os
# load the env keys
load_dotenv()

# db
db = SQLAlchemy()
app = Flask(__name__)

# this equals 50 MB memory size that the flask server can handle - 
# just for reference: when in prod we might need to set a limit to the server like
# Nginx -> client_max_body_size 50M; 
# or Gunicorn -> gunicorn --max-request-size 52428800
MEGABYTE = (2 ** 10) ** 2 #  50 MB memory size
app.config['MAX_CONTENT_LENGTH'] = 50 * MEGABYTE #  50 MB memory size
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * MEGABYTE #  50 MB memory size
# Configure the app 
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# for resume uploads
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'resume_upload')


def create_app():
    # Initialize the app
    db.init_app(app)
    # Initialize the socketio
    socketio.init_app(app)
    # Register blueprints
    from .views.frontend import frontend_bp
    from .api.jobs import jobs_bp
    from .api.direct_messages import direct_messages_bp
    from .api.notifications import notifications_bp
    from .api.applications import applications_bp
    from .api.profiles import profiles_bp
    
    app.register_blueprint(frontend_bp)
    app.register_blueprint(jobs_bp, url_prefix="/jobs/")
    app.register_blueprint(direct_messages_bp, url_prefix="/messages/")
    app.register_blueprint(notifications_bp, url_prefix="/notifications/")
    app.register_blueprint(applications_bp, url_prefix="/applications/")
    app.register_blueprint(profiles_bp, url_prefix="/profile/")
    # Initialize flask-login
    login_manager = LoginManager()
    login_manager.login_view = 'frontend.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        # Now we can simply query the unified User model
        from .models import User
        return User.query.get(int(user_id))

    
    # Import models to ensure they're known to SQLAlchemy
    from .models import User, Person, Company, Job, JobApplication, Room, Message
    
    # Create tables
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created!")
    
    return app
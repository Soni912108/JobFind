from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# local
from .extensions import socketio,mail
from .utils.logging import setup_logger
from .config.config import config_by_name

# Load environment variables
load_dotenv()

# Initialize database
db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    setup_logger(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'frontend.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
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
    
    # Create tables
    with app.app_context():
        from .models import User, Person, Company, Job, JobApplication, Room, Message
        app.logger.info("Database initialization: Starting table creation")
        db.create_all()
        app.logger.info("Database initialization: Tables created successfully")
    
    return app
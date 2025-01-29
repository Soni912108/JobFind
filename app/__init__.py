from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

app = Flask(__name__)

# Configure the app 
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:RrushKumbullaQepe%4030@jf_mysql_db/mydb"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:RrushKumbullaQepe%4030@jf_mysql_db/mydb"
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def create_app():
    # Initialize the app
    db.init_app(app)
    # Register blueprints
    from .views.frontend import frontend_bp
    from .api.jobs import jobs_bp
    from .api.direct_messages import direct_messages_bp
    from .api.notifications import notifications_bp
    from .api.applications import applications_bp
    
    app.register_blueprint(frontend_bp)
    app.register_blueprint(jobs_bp, url_prefix="/jobs/")
    app.register_blueprint(direct_messages_bp, url_prefix="/messages/")
    app.register_blueprint(notifications_bp, url_prefix="/notifications/")
    app.register_blueprint(applications_bp, url_prefix="/applications/")
    
    # Initialize flask-login
    login_manager = LoginManager()
    login_manager.login_view = 'frontend.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        user_type = session.get("user_type")
        print(f"User type on init file is: {user_type}")
        if user_type == "Person":
            return User.query.get(int(user_id))
        elif user_type == "Company":
            return Companies.query.get(int(user_id))
        return None

    
    # Import models to ensure they're known to SQLAlchemy
    from .models import User 
    from .models import Companies
    from .models import DirectMessages 
    from .models import Jobs 
    from .models import Notifications
    
    # Create tables
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created!")
    
    return app
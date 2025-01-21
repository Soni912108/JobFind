from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

app = Flask(__name__)

# Configure the app - connect to the database (NOTE: %40 is @ in url encoding)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:RrushKumbullaQepe%4030@jf_mysql_db/mydb"
app.config['SECRET_KEY'] = 'secret-key-goes-here'

def create_app():
    # Initialize the app
    db.init_app(app)
    
    # Register blueprints
    from .views.frontend import frontend_bp
    from .api.jobs import jobs_bp
    from .api.direct_messages import direct_messages_bp
    from .api.notifications import notifications_bp
    # Register blueprints
    app.register_blueprint(frontend_bp)
    app.register_blueprint(jobs_bp, url_prefix="/jobs/")
    app.register_blueprint(direct_messages_bp, url_prefix="/messages/")
    app.register_blueprint(notifications_bp, url_prefix="/notifications/")
    # Initialize flask-login
    login_manager = LoginManager()
    login_manager.login_view = 'frontend.users_login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Initialize database
    from .models import User
    from .models import Companies
    from .models import Jobs
    from .models import DirectMessages
    from .models import Notifications
    
    with app.app_context():
        print("Creating Databases")
        db.create_all()

    return app
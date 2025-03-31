import os
from datetime import timedelta

class Config:
    """Base config class"""
    # Basic Flask config
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # File upload config
    MEGABYTE = (2 ** 10) ** 2
    MAX_CONTENT_LENGTH = 50 * MEGABYTE
    MAX_FORM_MEMORY_SIZE = 50 * MEGABYTE
    
    # Database config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Mail config
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

class DevelopmentConfig(Config):
    """Development config"""
    DEBUG = True
    DEVELOPMENT = True
    UPLOAD_FOLDER = 'app/static/resume_upload'

class ProductionConfig(Config):
    """Production config"""
    DEBUG = False
    DEVELOPMENT = False
    UPLOAD_FOLDER = '/var/www/jobfind/static/resume_upload'  # Example production path

class TestingConfig(Config):
    """Testing config"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = 'tests/test_uploads'

# Dictionary to map config names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
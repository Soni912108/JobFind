from app import db
from flask_login import UserMixin
from sqlalchemy import DateTime
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import JSON
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import foreign



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(100), default='Person')  # Can be 'Company' or 'Person'
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    password = db.Column(db.String(1000))
    # more info that can be updated later on by the user
    skills = db.Column(JSON)
    experience = db.Column(JSON)
    location = db.Column(db.String(100))
    current_company_info = db.Column(JSON)
    # Timestamps for tracking
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Fix relationships
    sent_messages = db.relationship(
        'DirectMessages',
        primaryjoin="and_(foreign(DirectMessages.sender_id) == User.id, DirectMessages.sender_type == 'User')",
        backref='user_sender',
        lazy=True
    )
    received_messages = db.relationship(
        'DirectMessages',
        primaryjoin="and_(foreign(DirectMessages.receiver_id) == User.id, DirectMessages.receiver_type == 'User')",
        backref='user_receiver',
        lazy=True
    )




class Companies(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000))
    location = db.Column(db.String(100))
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship to jobs posted by the company
    jobs = db.relationship('Jobs', backref='company', lazy=True)


@dataclass
class Jobs(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)  # Foreign key to companies table
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    location = db.Column(db.String(100))
    salary = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

@dataclass
class DirectMessages(db.Model):
    __tablename__ = 'direct_messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False, index=True)
    sender_type = db.Column(db.String(50), nullable=False, index=True)  # 'User' or 'Company'
    receiver_id = db.Column(db.Integer, nullable=False, index=True)
    receiver_type = db.Column(db.String(50), nullable=False, index=True)  # 'User' or 'Company'
    message = db.Column(LONGTEXT)  # MySQL-specific long text field
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)




class Notifications(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, nullable=False) # Can be a user or a company
    message = db.Column(LONGTEXT)  # MySQL LONGTEXT for large messages
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)
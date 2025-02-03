from app import db
from flask_login import UserMixin
from sqlalchemy import DateTime
from datetime import datetime, date
from dataclasses import dataclass
from sqlalchemy import JSON
from sqlalchemy.dialects.mysql import LONGTEXT


class SimpleRepr(object):
    """A mixin implementing a simple __repr__."""
    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
            )

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    msg_id = db.Column(db.Integer, db.ForeignKey('direct_messages.id'), nullable=True)
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
    # sent_messages = db.relationship(
    #     'DirectMessages',
    #     primaryjoin="and_(foreign(DirectMessages.sender_id) == User.id, DirectMessages.sender_type == 'User')",
    #     backref='user_sender',
    #     lazy=True
    # )
    # received_messages = db.relationship(
    #     'DirectMessages',
    #     primaryjoin="and_(foreign(DirectMessages.receiver_id) == User.id, DirectMessages.receiver_type == 'User')",
    #     backref='user_receiver',
    #     lazy=True
    # )
    direct_messages = db.relationship('DirectMessages', backref='users', lazy=True)
    @property
    def role(self):
        return "Person"
    
    def __str__(self):
        return f"User: {self.name}, Email: {self.email}, Profession: {self.profession}"

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
            )

    def __json__(self):
        return {
            "id": self.id,
            "user_type": self.user_type,
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "profession": self.profession,
            "skills": self.skills,
            "experience": self.experience,
            "location": self.location,
            "current_company_info": self.current_company_info,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            
        }


class Companies(UserMixin,db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg_id = db.Column(db.Integer, db.ForeignKey('direct_messages.id'), nullable=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000)) # Hashed password
    description = db.Column(LONGTEXT) 
    location = db.Column(db.String(100))
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship to jobs posted by the company
    jobs = db.relationship('Jobs', backref='company', lazy=True)
    direct_messages = db.relationship('DirectMessages', backref='company', lazy=True)

    @property
    def role(self):
        return "Company"

    def __repr__(self):
        repr_str = f"{self.__class__.__name__}"
        repr_str += '('
        
        for key, val in self.__dict__.items():
            val= f"'{val}'" if isinstance(val, str) else val
            repr_str += f"{key}={val}, "
        
        return repr_str.strip(", ") + ')'
    
    def __json__(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            
        }

# Create association table
# applications = db.Table('applications',
#     db.Column('id', db.Integer,primary_key=True),
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('job_id', db.Integer, db.ForeignKey('jobs.id')),
#     # Need a column to store the resume of the user
    
#     db.Column('applied_at', DateTime, default=datetime.now)
# )

@dataclass
class Applications(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    # custom info for the application
    applied_at:datetime = db.Column(DateTime, default=datetime.now)
    resume = db.Column(LONGTEXT(collation='utf8mb4_unicode_ci')) # needs to change to proper datatype

    @property
    def calculate_days_applied(self):
        days = date(self.applied_at) - date.today()
        return f"Days passed from applied day {days}"

    def __json__(self):
        return {
            "id": self.id,
            "applied_at": self.applied_at,
            "resume": self.resume,  
        }

@dataclass
class Jobs(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)  # Foreign key to companies table
    title = db.Column(db.String(100))
    description = db.Column(LONGTEXT(collation='utf8mb4_unicode_ci'))  # Explicit collation
    location = db.Column(db.String(100))
    salary = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Add relationship to applicants
    applications = db.relationship('Applications', backref='application', lazy=True)

    def __json__(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "salary": self.salary,
            "location": self.location,
            "likes": self.likes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            
        }

@dataclass
class DirectMessages(db.Model):
    __tablename__ = 'direct_messages'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    sender_id = db.Column(db.Integer, nullable=False, index=True)
    sender_type = db.Column(db.String(50), nullable=False, index=True)  # 'User' or 'Company'
    receiver_id = db.Column(db.Integer, nullable=False, index=True)
    receiver_type = db.Column(db.String(50), nullable=False, index=True)  # 'User' or 'Company'
    message = db.Column(LONGTEXT)  # MySQL-specific long text field
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __json__(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type,
            "receiver_id": self.receiver_id,
            "receiver_type": self.receiver_type,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            
        }


class Notifications(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    receiver_id = db.Column(db.Integer, nullable=False) # Can be a user or a company
    message = db.Column(LONGTEXT)  # MySQL LONGTEXT for large messages
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.now)
    updated_at = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __json__(self):
        return {
            "id": self.id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            
        }
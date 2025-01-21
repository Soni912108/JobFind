from flask import Blueprint, request, flash, redirect, url_for
from app import db
from app.models import User, Companies, Jobs
from datetime import datetime
from flask_login import login_user,login_required, current_user, logout_user

direct_messages_bp = Blueprint("direct_messages",__name__)
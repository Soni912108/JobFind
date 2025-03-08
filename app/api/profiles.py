from flask import Blueprint, request, flash, redirect, url_for, jsonify
from app import db
from app.models import Person, Company, Job, JobApplication
from datetime import datetime
from flask_login import login_required, current_user

profiles_bp = Blueprint("profiles", __name__)

# here will add rest api to edit profile